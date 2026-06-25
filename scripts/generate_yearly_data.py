#!/usr/bin/env python3
"""
Generate a single SQL file with daily cumulative usage data for a full year.
Each month has different costs and usage patterns.
All instance/volume IDs are preserved from the original file.
"""

import json
import copy
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import calendar


# Default service ID from the file name
DEFAULT_SERVICE_ID = "b41a8077d3ed49c69ddc77ed0b16572e"


def parse_date(date_str: str) -> datetime:
    """Parse ISO format date string to datetime."""
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


def format_date(dt: datetime) -> str:
    """Format datetime to ISO string with Z suffix."""
    return dt.isoformat().replace('+00:00', 'Z')


def get_monthly_multiplier(month: int, year: int) -> float:
    """
    Get a multiplier for each month to create different costs.
    Returns a value between 0.5 and 1.8.
    """
    # Base multipliers for each month (seasonal patterns)
    # January: 0.8, February: 0.7, March: 0.9, April: 1.0, May: 1.1, June: 1.2
    # July: 1.3, August: 1.4, September: 1.2, October: 1.1, November: 1.0, December: 0.9
    seasonal = {
        1: 0.8,   # January - post-holiday slowdown
        2: 0.7,   # February - slowest month
        3: 0.9,   # March - starting to pick up
        4: 1.0,   # April - steady
        5: 1.1,   # May - growing
        6: 1.2,   # June - strong
        7: 1.3,   # July - peak summer
        8: 1.4,   # August - highest usage
        9: 1.2,   # September - still strong
        10: 1.1,  # October - steady
        11: 1.0,  # November - stable
        12: 0.9   # December - holiday slowdown
    }
    
    # Add some randomness to make it more realistic
    random_factor = 0.85 + (random.random() * 0.30)  # 0.85 to 1.15
    
    return seasonal.get(month, 1.0) * random_factor


def generate_daily_usage_for_month(
    base_data: Dict[str, Any],
    year: int,
    month: int,
    month_multiplier: float,
    service_id: str
) -> str:
    """
    Generate SQL inserts for all days in a month.
    
    Args:
        base_data: The base monthly usage data (final totals)
        year: The year to generate data for
        month: The month to generate data for (1-12)
        month_multiplier: Multiplier for this month's costs
        service_id: Service ID to use for all entries
    
    Returns:
        SQL string with all inserts for this month
    """
    # Parse the base period
    base_period_from = parse_date(base_data["period"]["from"])
    base_total = base_data["totalPrice"]["value"]
    
    # Calculate month start and end
    month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=base_period_from.tzinfo)
    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime(year, month, last_day, 0, 0, 0, tzinfo=base_period_from.tzinfo) + timedelta(days=1)
    
    # Calculate days in this month
    total_days = (month_end - month_start).days
    
    # Generate a random growth pattern for this month
    # Different months will have different growth curves
    growth_pattern = random.choice([
        "early",    # Fast growth early, then plateau
        "late",     # Slow growth early, then accelerate
        "steady",   # Steady growth throughout
        "s-curve"   # S-curve growth
    ])
    
    sql_parts = []
    
    for day_idx in range(total_days):
        target_date = month_start + timedelta(days=day_idx)
        
        # Calculate the cumulative percentage for this day based on the growth pattern
        progress = (day_idx + 1) / total_days
        
        if growth_pattern == "early":
            # Fast growth early, plateau later
            percentage = 0.3 + (0.7 * (progress ** 0.5))
        elif growth_pattern == "late":
            # Slow growth early, accelerate later
            percentage = progress ** 1.5
        elif growth_pattern == "steady":
            # Steady linear growth
            percentage = progress
        else:  # s-curve
            # S-curve: starts slow, accelerates, then slows down
            t = progress
            percentage = (t ** 3) / ((t ** 3) + ((1 - t) ** 3))
        
        # Add some daily variation
        daily_variation = 0.95 + (random.random() * 0.10)  # 0.95 to 1.05
        percentage = percentage * daily_variation
        
        # Ensure we don't go over 100% on the last day
        if day_idx == total_days - 1:
            percentage = 1.0
        
        # Clamp to reasonable bounds
        percentage = max(0.01, min(1.0, percentage))
        
        # Apply monthly multiplier
        monthly_total = base_total * month_multiplier
        cumulative_total = monthly_total * percentage
        
        # Deep copy and modify the data
        data = copy.deepcopy(base_data)
        
        # Update period (full month)
        data["period"]["from"] = format_date(month_start)
        data["period"]["to"] = format_date(month_end)
        
        # Update lastUpdate
        data["lastUpdate"] = format_date(target_date.replace(
            hour=12, minute=0, second=0, microsecond=0
        ))
        
        # Scale the total price
        if "totalPrice" in data and "value" in data["totalPrice"]:
            data["totalPrice"]["value"] = cumulative_total
            data["totalPrice"]["text"] = f"{cumulative_total:.2f} EUR"
            data["totalPrice"]["priceInUcents"] = int(cumulative_total * 10000000000)
        
        # Scale all components
        _scale_all_components(data, percentage, month_multiplier)
        
        # Generate SQL insert
        sql = generate_sql_insert(data, target_date, service_id, cumulative_total)
        sql_parts.append(sql)
    
    return "\n".join(sql_parts)


def _scale_all_components(data: Dict[str, Any], daily_percentage: float, month_multiplier: float) -> None:
    """Scale all components in the data structure."""
    # Scale hourly usage (volumes)
    if "hourlyUsage" in data and "volume" in data["hourlyUsage"]:
        for volume_group in data["hourlyUsage"]["volume"]:
            _scale_volume_group_cumulative(volume_group, daily_percentage, month_multiplier)
    
    # Scale storage
    if "hourlyUsage" in data and "storage" in data["hourlyUsage"]:
        for storage in data["hourlyUsage"]["storage"]:
            _scale_storage_cumulative(storage, daily_percentage, month_multiplier)
    
    # Scale hourly instances
    if "hourlyUsage" in data and "instance" in data["hourlyUsage"]:
        for instance_group in data["hourlyUsage"]["instance"]:
            _scale_instance_group_cumulative(instance_group, daily_percentage, month_multiplier)
    
    # Scale monthly instances
    if "monthlyUsage" in data and "instance" in data["monthlyUsage"]:
        for instance_group in data["monthlyUsage"]["instance"]:
            _scale_monthly_instance_group_cumulative(instance_group, daily_percentage, month_multiplier)
    
    # Scale savings plans
    if "monthlyUsage" in data and "savingsPlan" in data["monthlyUsage"]:
        for plan_group in data["monthlyUsage"]["savingsPlan"]:
            _scale_savings_plan_group_cumulative(plan_group, daily_percentage, month_multiplier)
    
    # Scale resourcesUsage
    if "resourcesUsage" in data:
        for resource in data["resourcesUsage"]:
            _scale_resource_cumulative(resource, daily_percentage, month_multiplier)


def _scale_volume_group_cumulative(group: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale a volume group cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * total_multiplier)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * total_multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * total_multiplier)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * total_multiplier


def _scale_storage_cumulative(storage: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale storage cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "stored" in storage and "quantity" in storage["stored"]:
        if "value" in storage["stored"]["quantity"]:
            storage["stored"]["quantity"]["value"] = storage["stored"]["quantity"]["value"] * total_multiplier
        if "totalPrice" in storage["stored"]:
            storage["stored"]["totalPrice"] = storage["stored"]["totalPrice"] * total_multiplier
    
    if "totalPrice" in storage:
        storage["totalPrice"] = storage["totalPrice"] * total_multiplier


def _scale_instance_group_cumulative(group: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale an instance group cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * total_multiplier)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * total_multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * total_multiplier)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * total_multiplier


def _scale_monthly_instance_group_cumulative(group: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale monthly instance values cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * total_multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * total_multiplier


def _scale_savings_plan_group_cumulative(group: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale savings plan values cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "totalPrice" in group:
        if isinstance(group["totalPrice"], dict) and "value" in group["totalPrice"]:
            group["totalPrice"]["value"] = group["totalPrice"]["value"] * total_multiplier
            group["totalPrice"]["text"] = f"{group['totalPrice']['value']:.2f} EUR"
            group["totalPrice"]["priceInUcents"] = int(group["totalPrice"]["value"] * 10000000000)
        else:
            group["totalPrice"] = group["totalPrice"] * total_multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "totalPrice" in detail:
                if isinstance(detail["totalPrice"], dict) and "value" in detail["totalPrice"]:
                    detail["totalPrice"]["value"] = detail["totalPrice"]["value"] * total_multiplier
                    detail["totalPrice"]["text"] = f"{detail['totalPrice']['value']:.2f} EUR"
                    detail["totalPrice"]["priceInUcents"] = int(detail["totalPrice"]["value"] * 10000000000)
                else:
                    detail["totalPrice"] = detail["totalPrice"] * total_multiplier


def _scale_resource_cumulative(resource: Dict[str, Any], percentage: float, month_multiplier: float) -> None:
    """Scale resource usage cumulatively."""
    total_multiplier = percentage * month_multiplier
    
    if "totalPrice" in resource:
        resource["totalPrice"] = resource["totalPrice"] * total_multiplier
    
    if "resources" in resource:
        for res in resource["resources"]:
            if "components" in res:
                for comp in res["components"]:
                    if "quantity" in comp and "value" in comp["quantity"]:
                        comp["quantity"]["value"] = int(comp["quantity"]["value"] * total_multiplier)
                    if "totalPrice" in comp:
                        comp["totalPrice"] = comp["totalPrice"] * total_multiplier


def generate_sql_insert(data: Dict[str, Any], target_date: datetime, service_id: str, total_price: float) -> str:
    """Generate a SQL INSERT statement for the current_usage_raw table."""
    json_str = json.dumps(data).replace("'", "''")
    
    # Format timestamps for PostgreSQL
    period_from = data["period"]["from"].replace('Z', '+00:00')
    period_to = data["period"]["to"].replace('Z', '+00:00')
    last_update = data["lastUpdate"].replace('Z', '+00:00')
    call_timestamp = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', '+00:00')
    
    sql = f"""INSERT INTO current_usage_raw (
    service_id,
    period_from,
    period_to,
    call_timestamp,
    last_update,
    total_price,
    total_price_currency,
    full_response_json,
    created_at
) VALUES (
    '{service_id}',
    '{period_from}',
    '{period_to}',
    '{call_timestamp}',
    '{last_update}',
    {total_price:.6f},
    'EUR',
    '{json_str}'::jsonb,
    NOW()
);"""
    return sql


def generate_yearly_sql(
    input_file: str,
    output_file: str,
    year: int,
    service_id: str,
    seed: Optional[int] = None
) -> None:
    """
    Generate a single SQL file with all daily data for a year.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output SQL file
        year: The year to generate data for
        service_id: Service ID to use for all entries
        seed: Optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    # Read input file
    with open(input_file, 'r') as f:
        base_data = json.load(f)
    
    print(f"\n{'='*70}")
    print(f"Generating daily usage data for year {year}")
    print(f"Service ID: {service_id}")
    print(f"Based on monthly template: {input_file}")
    print(f"{'='*70}\n")
    
    all_sql_parts = []
    total_days = 0
    
    # Generate data for each month
    for month in range(1, 13):
        # Get a different multiplier for each month
        month_multiplier = get_monthly_multiplier(month, year)
        month_name = datetime(year, month, 1).strftime('%B')
        
        print(f"Generating {month_name} (multiplier: {month_multiplier:.2f})...")
        
        # Generate SQL for this month
        month_sql = generate_daily_usage_for_month(
            base_data,
            year,
            month,
            month_multiplier,
            service_id
        )
        
        all_sql_parts.append(f"-- ============================================")
        all_sql_parts.append(f"-- {month_name} {year}")
        all_sql_parts.append(f"-- Monthly multiplier: {month_multiplier:.2f}")
        all_sql_parts.append(f"-- ============================================")
        all_sql_parts.append(month_sql)
        
        # Count days in this month
        last_day = calendar.monthrange(year, month)[1]
        total_days += last_day
    
    # Write the combined SQL file
    print(f"\nWriting SQL file: {output_file}")
    
    with open(output_file, 'w') as f:
        f.write(f"-- ============================================================\n")
        f.write(f"-- Combined SQL inserts for year {year}\n")
        f.write(f"-- Service ID: {service_id}\n")
        f.write(f"-- Total days: {total_days}\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- ============================================================\n\n")
        f.write("BEGIN;\n\n")
        f.write("\n".join(all_sql_parts))
        f.write("\n\nCOMMIT;\n")
    
    print(f"\n{'='*70}")
    print(f"Done! Generated {total_days} daily records")
    print(f"SQL file: {output_file}")
    print(f"File size: {Path(output_file).stat().st_size / 1024 / 1024:.2f} MB")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a single SQL file with daily cumulative usage data for a year"
    )
    parser.add_argument(
        "input_file",
        help="Path to the input JSON file"
    )
    parser.add_argument(
        "-o", "--output-file",
        default="./yearly_usage.sql",
        help="Path to the output SQL file (default: ./yearly_usage.sql)"
    )
    parser.add_argument(
        "-y", "--year",
        type=int,
        default=datetime.now().year,
        help=f"Year to generate data for (default: {datetime.now().year})"
    )
    parser.add_argument(
        "-s", "--service-id",
        default=DEFAULT_SERVICE_ID,
        help=f"Service ID to use for all entries (default: {DEFAULT_SERVICE_ID})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    # If service ID is still the placeholder, warn the user
    if args.service_id == "example-service-id":
        print("WARNING: Using placeholder service_id 'example-service-id'")
        print(f"Use -s to set the correct service ID (default: {DEFAULT_SERVICE_ID})")
        response = input("Continue with 'example-service-id'? (y/N): ")
        if response.lower() != 'y':
            print("Aborting. Please provide the correct service ID.")
            return
    
    generate_yearly_sql(
        args.input_file,
        args.output_file,
        args.year,
        args.service_id,
        args.seed
    )


if __name__ == "__main__":
    main()