"""
Generate a single SQL file with daily cumulative usage data for a full year.
Each month has different costs and usage patterns.
All instance/volume IDs are preserved from the original file.
IMPORTANT: Values are strictly cumulative (monotonically increasing) within each month.
"""

import json
import copy
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List
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


def generate_cumulative_percentages(total_days: int, growth_pattern: str, seed_offset: int) -> List[float]:
    """
    Generate strictly increasing cumulative percentages for each day in a month.
    """
    # Set a deterministic seed for this month to ensure reproducible patterns
    random.seed(seed_offset)
    
    percentages = []
    
    for day_idx in range(total_days):
        progress = (day_idx + 1) / total_days
        
        if growth_pattern == "early":
            # Fast growth early, plateau later
            raw_pct = 0.3 + (0.7 * (progress ** 0.5))
        elif growth_pattern == "late":
            # Slow growth early, accelerate later
            raw_pct = progress ** 1.5
        elif growth_pattern == "steady":
            # Steady linear growth
            raw_pct = progress
        else:  # s-curve
            # S-curve: starts slow, accelerates, then slows down
            t = progress
            raw_pct = (t ** 3) / ((t ** 3) + ((1 - t) ** 3))
        
        # Add small daily variation, but ensure it doesn't break monotonicity
        # We'll apply the variation after we ensure the sequence is increasing
        percentages.append(raw_pct)
    
    # Ensure strictly increasing and between 1% and 100%
    for i in range(1, len(percentages)):
        if percentages[i] <= percentages[i-1]:
            # Add a small increment to ensure it's strictly increasing
            percentages[i] = percentages[i-1] + 0.001
        
        # Cap at 100%
        if percentages[i] > 1.0:
            percentages[i] = 1.0
    
    # Ensure first day is at least 1% and last day is exactly 100%
    percentages[0] = max(0.01, percentages[0])
    percentages[-1] = 1.0
    
    # Add slight daily variation (1-3%) but maintain monotonicity
    for i in range(1, len(percentages) - 1):
        variation = 0.98 + (random.random() * 0.04)  # 0.98 to 1.02
        new_val = percentages[i] * variation
        # Ensure it's between previous and next values
        if new_val <= percentages[i-1]:
            new_val = percentages[i-1] + 0.001
        if new_val >= percentages[i+1]:
            new_val = percentages[i+1] - 0.001
        percentages[i] = new_val
    
    # Final pass to ensure strict monotonicity
    for i in range(1, len(percentages)):
        if percentages[i] <= percentages[i-1]:
            percentages[i] = percentages[i-1] + 0.001
    
    return percentages


def adjust_savings_plans(
    data: Dict[str, Any], 
    month_start: datetime, 
    month_end: datetime,
    plan_multiplier: float
) -> None:
    """
    Adjust savings plan dates and prices to span across months realistically.
    """
    if "monthlyUsage" not in data or "savingsPlan" not in data["monthlyUsage"]:
        return
    
    # Get the base savings plan data
    savings_plans = data["monthlyUsage"]["savingsPlan"]
    
    for plan_group in savings_plans:
        if "details" not in plan_group:
            continue
        
        # Generate new plan dates that span multiple months
        for detail in plan_group["details"]:
            # Randomly decide plan duration (1-6 months)
            duration_months = random.randint(1, 6)
            
            # Random start month (could be before or after current month)
            start_month_offset = random.randint(-2, 2)
            
            # Calculate start date with proper month handling
            target_month = month_start.month + start_month_offset
            target_year = month_start.year
            
            # Adjust year if month goes beyond 12 or below 1
            if target_month > 12:
                target_month = target_month - 12
                target_year = target_year + 1
            elif target_month < 1:
                target_month = target_month + 12
                target_year = target_year - 1
            
            # Ensure we don't go below the year start
            if target_year < month_start.year:
                target_year = month_start.year
                target_month = 1
            
            plan_start = datetime(
                target_year, 
                target_month, 
                1, 
                0, 0, 0, 
                tzinfo=month_start.tzinfo
            )
            
            # Calculate end date
            end_month = plan_start.month + duration_months
            end_year = plan_start.year
            
            # Adjust year if month goes beyond 12
            while end_month > 12:
                end_month = end_month - 12
                end_year = end_year + 1
            
            # If end is before the month_end, extend it
            plan_end = datetime(
                end_year, 
                min(end_month, 12), 
                1, 
                0, 0, 0, 
                tzinfo=month_start.tzinfo
            )
            
            # Ensure end is at least the current month end + some days
            if plan_end <= month_end:
                # Add 1-3 months
                extra_months = random.randint(1, 3)
                temp_month = plan_end.month + extra_months
                temp_year = plan_end.year
                while temp_month > 12:
                    temp_month = temp_month - 12
                    temp_year = temp_year + 1
                plan_end = datetime(
                    temp_year,
                    min(temp_month, 12),
                    1,
                    0, 0, 0,
                    tzinfo=month_start.tzinfo
                )
            
            # Set the period
            detail["period"]["from"] = format_date(plan_start)
            detail["period"]["to"] = format_date(plan_end)
            
            # Calculate prorated price for this month
            total_plan_days = (plan_end - plan_start).days
            days_in_month = (month_end - month_start).days
            
            # Get original plan price
            if "unitPrice" in detail and isinstance(detail["unitPrice"], dict):
                original_price = detail["unitPrice"]["value"]
            elif "totalPrice" in detail and isinstance(detail["totalPrice"], dict):
                original_price = detail["totalPrice"]["value"]
            else:
                continue
            
            # Prorate the price for this month
            if total_plan_days > 0:
                prorated_price = original_price * (days_in_month / max(total_plan_days, 1))
                prorated_price *= plan_multiplier
            else:
                prorated_price = original_price * plan_multiplier
            
            # Update total price for this month
            if "totalPrice" in detail:
                if isinstance(detail["totalPrice"], dict):
                    detail["totalPrice"]["value"] = prorated_price
                    detail["totalPrice"]["text"] = f"{prorated_price:.2f} EUR"
                    detail["totalPrice"]["priceInUcents"] = int(prorated_price * 10000000000)
                else:
                    detail["totalPrice"] = prorated_price
    
    # Update the total price for the plan group
    for plan_group in savings_plans:
        total = 0
        if "details" in plan_group:
            for detail in plan_group["details"]:
                if "totalPrice" in detail:
                    if isinstance(detail["totalPrice"], dict):
                        total += detail["totalPrice"]["value"]
                    else:
                        total += detail["totalPrice"]
        
        if "totalPrice" in plan_group:
            if isinstance(plan_group["totalPrice"], dict):
                plan_group["totalPrice"]["value"] = total
                plan_group["totalPrice"]["text"] = f"{total:.2f} EUR"
                plan_group["totalPrice"]["priceInUcents"] = int(total * 10000000000)
            else:
                plan_group["totalPrice"] = total


def generate_daily_usage_for_month(
    base_data: Dict[str, Any],
    year: int,
    month: int,
    month_multiplier: float,
    service_id: str,
    month_seed: int
) -> str:
    """
    Generate SQL inserts for all days in a month.
    
    Args:
        base_data: The base monthly usage data (final totals)
        year: The year to generate data for
        month: The month to generate data for (1-12)
        month_multiplier: Multiplier for this month's costs
        service_id: Service ID to use for all entries
        month_seed: Seed for deterministic random generation
    
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
    
    # Choose growth pattern deterministically based on month
    patterns = ["early", "late", "steady", "s-curve"]
    growth_pattern = patterns[(month - 1) % len(patterns)]
    
    # Generate strictly increasing cumulative percentages
    cumulative_percentages = generate_cumulative_percentages(
        total_days, 
        growth_pattern, 
        month_seed
    )
    
    sql_parts = []
    
    for day_idx in range(total_days):
        target_date = month_start + timedelta(days=day_idx)
        
        # Get the cumulative percentage for this day (strictly increasing)
        percentage = cumulative_percentages[day_idx]
        
        # Apply monthly multiplier
        monthly_total = base_total * month_multiplier
        cumulative_total = monthly_total * percentage
        
        # Deep copy and modify the data
        data = copy.deepcopy(base_data)
        
        # Update period (full month)
        data["period"]["from"] = format_date(month_start)
        data["period"]["to"] = format_date(month_end)
        
        # Adjust savings plans for this month (with different durations and dates)
        # Use a different seed for savings plans to vary them
        random.seed(month_seed + 1000)
        adjust_savings_plans(data, month_start, month_end, month_multiplier)
        
        # Update lastUpdate to the target date
        data["lastUpdate"] = format_date(target_date.replace(
            hour=12, minute=0, second=0, microsecond=0
        ))
        
        # Scale the total price (cumulative)
        if "totalPrice" in data and "value" in data["totalPrice"]:
            data["totalPrice"]["value"] = cumulative_total
            data["totalPrice"]["text"] = f"{cumulative_total:.2f} EUR"
            data["totalPrice"]["priceInUcents"] = int(cumulative_total * 10000000000)
        
        # Scale all components (except savings plans which we already handled)
        _scale_all_components_except_savings(data, percentage, month_multiplier)
        
        # Generate SQL insert with created_at matching the data date
        sql = generate_sql_insert(data, target_date, service_id, cumulative_total)
        sql_parts.append(sql)
    
    return "\n".join(sql_parts)


def _scale_all_components_except_savings(
    data: Dict[str, Any], 
    daily_percentage: float, 
    month_multiplier: float
) -> None:
    """Scale all components except savings plans (already handled separately)."""
    total_multiplier = daily_percentage * month_multiplier
    
    # Scale hourly usage (volumes)
    if "hourlyUsage" in data and "volume" in data["hourlyUsage"]:
        for volume_group in data["hourlyUsage"]["volume"]:
            _scale_volume_group(volume_group, total_multiplier)
    
    # Scale storage
    if "hourlyUsage" in data and "storage" in data["hourlyUsage"]:
        for storage in data["hourlyUsage"]["storage"]:
            _scale_storage(storage, total_multiplier)
    
    # Scale hourly instances
    if "hourlyUsage" in data and "instance" in data["hourlyUsage"]:
        for instance_group in data["hourlyUsage"]["instance"]:
            _scale_instance_group(instance_group, total_multiplier)
    
    # Scale monthly instances
    if "monthlyUsage" in data and "instance" in data["monthlyUsage"]:
        for instance_group in data["monthlyUsage"]["instance"]:
            _scale_monthly_instance_group(instance_group, total_multiplier)
    
    # Scale resourcesUsage
    if "resourcesUsage" in data:
        for resource in data["resourcesUsage"]:
            _scale_resource(resource, total_multiplier)


def _scale_volume_group(group: Dict[str, Any], multiplier: float) -> None:
    """Scale a volume group."""
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * multiplier)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * multiplier)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * multiplier


def _scale_storage(storage: Dict[str, Any], multiplier: float) -> None:
    """Scale storage."""
    if "stored" in storage and "quantity" in storage["stored"]:
        if "value" in storage["stored"]["quantity"]:
            storage["stored"]["quantity"]["value"] = storage["stored"]["quantity"]["value"] * multiplier
        if "totalPrice" in storage["stored"]:
            storage["stored"]["totalPrice"] = storage["stored"]["totalPrice"] * multiplier
    
    if "totalPrice" in storage:
        storage["totalPrice"] = storage["totalPrice"] * multiplier


def _scale_instance_group(group: Dict[str, Any], multiplier: float) -> None:
    """Scale an instance group."""
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * multiplier)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * multiplier)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * multiplier


def _scale_monthly_instance_group(group: Dict[str, Any], multiplier: float) -> None:
    """Scale monthly instance values."""
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * multiplier
    
    if "details" in group:
        for detail in group["details"]:
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * multiplier


def _scale_resource(resource: Dict[str, Any], multiplier: float) -> None:
    """Scale resource usage."""
    if "totalPrice" in resource:
        resource["totalPrice"] = resource["totalPrice"] * multiplier
    
    if "resources" in resource:
        for res in resource["resources"]:
            if "components" in res:
                for comp in res["components"]:
                    if "quantity" in comp and "value" in comp["quantity"]:
                        comp["quantity"]["value"] = int(comp["quantity"]["value"] * multiplier)
                    if "totalPrice" in comp:
                        comp["totalPrice"] = comp["totalPrice"] * multiplier


def generate_sql_insert(data: Dict[str, Any], target_date: datetime, service_id: str, total_price: float) -> str:
    """Generate a SQL INSERT statement for the current_usage_raw table."""
    json_str = json.dumps(data).replace("'", "''")
    
    # Format timestamps for PostgreSQL
    period_from = data["period"]["from"].replace('Z', '+00:00')
    period_to = data["period"]["to"].replace('Z', '+00:00')
    last_update = data["lastUpdate"].replace('Z', '+00:00')
    call_timestamp = target_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace('+00:00', '+00:00')
    
    # Set created_at to the same day as the data (with a random time during the day)
    random_hour = random.randint(9, 17)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    created_at = target_date.replace(
        hour=random_hour, 
        minute=random_minute, 
        second=random_second, 
        microsecond=random.randint(0, 999999)
    ).isoformat().replace('+00:00', '+00:00')
    
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
    '{created_at}'
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
        
        # Use a unique seed for each month to ensure different patterns but reproducible
        month_seed = (year * 100) + month + (seed if seed else 0)
        
        print(f"Generating {month_name} (multiplier: {month_multiplier:.2f})...")
        
        # Generate SQL for this month
        month_sql = generate_daily_usage_for_month(
            base_data,
            year,
            month,
            month_multiplier,
            service_id,
            month_seed
        )
        
        all_sql_parts.append(f"-- ============================================")
        all_sql_parts.append(f"-- {month_name} {year}")
        all_sql_parts.append(f"-- Monthly multiplier: {month_multiplier:.2f}")
        all_sql_parts.append(f"-- Growth pattern: {['early', 'late', 'steady', 's-curve'][(month-1)%4]}")
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
        f.write(f"-- ============================================================\n")
        f.write(f"-- IMPORTANT: Values are CUMULATIVE (monotonically increasing)\n")
        f.write(f"-- To get daily values, use LAG() or difference between days\n")
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