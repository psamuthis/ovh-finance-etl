#!/usr/bin/env python3
"""
Generate daily cumulative usage files from a monthly usage JSON file.
Each day's data represents the cumulative total from the start of the month.
"""

import json
import copy
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
import argparse


# Default service ID from the file name
DEFAULT_SERVICE_ID = "b41a8077d3ed49c69ddc77ed0b16572e"


def parse_date(date_str: str) -> datetime:
    """Parse ISO format date string to datetime."""
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


def format_date(dt: datetime) -> str:
    """Format datetime to ISO string with Z suffix."""
    return dt.isoformat().replace('+00:00', 'Z')


def format_datetime_for_postgres(dt: datetime) -> str:
    """Format datetime for PostgreSQL TIMESTAMPTZ."""
    # PostgreSQL accepts either '2026-06-30T00:00:00+00:00' or '2026-06-30T00:00:00Z'
    # Let's use the format without Z and with +00:00
    return dt.isoformat().replace('+00:00', '+00:00')


def generate_cumulative_daily_usage(
    base_data: Dict[str, Any],
    target_date: datetime,
    month_start: datetime,
    month_end: datetime,
    day_index: int,
    total_days: int
) -> Dict[str, Any]:
    """
    Generate cumulative usage data for a specific day.
    
    The data for each day represents the cumulative total from day 1 to that day.
    Each day's total is slightly higher than the previous day's total.
    
    Args:
        base_data: The base monthly usage data (final totals)
        target_date: The date for which to generate data
        month_start: Start of the month (period_from)
        month_end: End of the month (period_to)
        day_index: 0-based index of the day in the month
        total_days: Total number of days in the month
    
    Returns:
        Cumulative usage data for the specific day
    """
    # Deep copy to avoid modifying the original
    data = copy.deepcopy(base_data)
    
    # Calculate the cumulative percentage for this day
    # Day 1: ~3-5% of total, Day N (last day): 100% of total
    progress = (day_index + 1) / total_days  # 1/total_days to 1.0
    
    # Start at 3-5% on day 1, end at 100% on last day
    if day_index == 0:
        # First day: 3-5% of total
        percentage = 0.03 + (random.random() * 0.02)
    else:
        # S-curve: starts slow, accelerates, then slows down near the end
        t = progress
        # Sigmoid-like curve
        smooth = (t ** 3) / ((t ** 3) + ((1 - t) ** 3))
        # Add some random variation
        variation = 0.97 + (random.random() * 0.06)
        percentage = smooth * variation
        
        # Ensure we don't go over 100% on the last day
        if day_index == total_days - 1:
            percentage = 1.0
    
    # Clamp to reasonable bounds
    percentage = max(0.01, min(1.0, percentage))
    
    # Keep the period as the full month (not the day)
    data["period"]["from"] = format_date(month_start)
    data["period"]["to"] = format_date(month_end)
    
    # Update lastUpdate to the target date
    data["lastUpdate"] = format_date(target_date.replace(
        hour=12, minute=0, second=0, microsecond=0
    ))
    
    # Scale the total price (cumulative)
    if "totalPrice" in data and "value" in data["totalPrice"]:
        original_total = data["totalPrice"]["value"]
        cumulative_total = original_total * percentage
        data["totalPrice"]["value"] = cumulative_total
        data["totalPrice"]["text"] = f"{cumulative_total:.2f} EUR"
        data["totalPrice"]["priceInUcents"] = int(cumulative_total * 10000000000)
    
    # Scale hourly usage (volumes) - cumulative
    if "hourlyUsage" in data and "volume" in data["hourlyUsage"]:
        for volume_group in data["hourlyUsage"]["volume"]:
            _scale_volume_group_cumulative(volume_group, percentage)
    
    # Scale storage - cumulative
    if "hourlyUsage" in data and "storage" in data["hourlyUsage"]:
        for storage in data["hourlyUsage"]["storage"]:
            _scale_storage_cumulative(storage, percentage)
    
    # Scale hourly instances - cumulative
    if "hourlyUsage" in data and "instance" in data["hourlyUsage"]:
        for instance_group in data["hourlyUsage"]["instance"]:
            _scale_instance_group_cumulative(instance_group, percentage)
    
    # Scale monthly instances - cumulative
    if "monthlyUsage" in data and "instance" in data["monthlyUsage"]:
        for instance_group in data["monthlyUsage"]["instance"]:
            _scale_monthly_instance_group_cumulative(instance_group, percentage)
    
    # Scale savings plans - cumulative
    if "monthlyUsage" in data and "savingsPlan" in data["monthlyUsage"]:
        for plan_group in data["monthlyUsage"]["savingsPlan"]:
            _scale_savings_plan_group_cumulative(plan_group, percentage)
    
    # Scale resourcesUsage - cumulative
    if "resourcesUsage" in data:
        for resource in data["resourcesUsage"]:
            _scale_resource_cumulative(resource, percentage)
    
    return data


def _scale_volume_group_cumulative(group: Dict[str, Any], percentage: float) -> None:
    """Scale a volume group cumulatively - keep all IDs unchanged."""
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * percentage)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * percentage
    
    if "details" in group:
        for detail in group["details"]:
            # Keep volumeId and resourceId unchanged
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * percentage)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * percentage


def _scale_storage_cumulative(storage: Dict[str, Any], percentage: float) -> None:
    """Scale storage cumulatively."""
    if "stored" in storage and "quantity" in storage["stored"]:
        if "value" in storage["stored"]["quantity"]:
            storage["stored"]["quantity"]["value"] = storage["stored"]["quantity"]["value"] * percentage
        if "totalPrice" in storage["stored"]:
            storage["stored"]["totalPrice"] = storage["stored"]["totalPrice"] * percentage
    
    if "totalPrice" in storage:
        storage["totalPrice"] = storage["totalPrice"] * percentage


def _scale_instance_group_cumulative(group: Dict[str, Any], percentage: float) -> None:
    """Scale an instance group cumulatively - keep all IDs unchanged."""
    if "quantity" in group and "value" in group["quantity"]:
        group["quantity"]["value"] = int(group["quantity"]["value"] * percentage)
    
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * percentage
    
    if "details" in group:
        for detail in group["details"]:
            # Keep instanceId and resourceId unchanged
            if "quantity" in detail and "value" in detail["quantity"]:
                detail["quantity"]["value"] = int(detail["quantity"]["value"] * percentage)
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * percentage


def _scale_monthly_instance_group_cumulative(group: Dict[str, Any], percentage: float) -> None:
    """Scale monthly instance values cumulatively."""
    if "totalPrice" in group:
        group["totalPrice"] = group["totalPrice"] * percentage
    
    if "details" in group:
        for detail in group["details"]:
            # Keep instanceId and resourceId unchanged
            if "totalPrice" in detail:
                detail["totalPrice"] = detail["totalPrice"] * percentage


def _scale_savings_plan_group_cumulative(group: Dict[str, Any], percentage: float) -> None:
    """Scale savings plan values cumulatively."""
    if "totalPrice" in group:
        if isinstance(group["totalPrice"], dict) and "value" in group["totalPrice"]:
            group["totalPrice"]["value"] = group["totalPrice"]["value"] * percentage
            group["totalPrice"]["text"] = f"{group['totalPrice']['value']:.2f} EUR"
            group["totalPrice"]["priceInUcents"] = int(group["totalPrice"]["value"] * 10000000000)
        else:
            group["totalPrice"] = group["totalPrice"] * percentage
    
    if "details" in group:
        for detail in group["details"]:
            # Keep plan IDs unchanged
            if "totalPrice" in detail:
                if isinstance(detail["totalPrice"], dict) and "value" in detail["totalPrice"]:
                    detail["totalPrice"]["value"] = detail["totalPrice"]["value"] * percentage
                    detail["totalPrice"]["text"] = f"{detail['totalPrice']['value']:.2f} EUR"
                    detail["totalPrice"]["priceInUcents"] = int(detail["totalPrice"]["value"] * 10000000000)
                else:
                    detail["totalPrice"] = detail["totalPrice"] * percentage


def _scale_resource_cumulative(resource: Dict[str, Any], percentage: float) -> None:
    """Scale resource usage cumulatively."""
    if "totalPrice" in resource:
        resource["totalPrice"] = resource["totalPrice"] * percentage
    
    if "resources" in resource:
        for res in resource["resources"]:
            if "components" in res:
                for comp in res["components"]:
                    # Keep resource IDs unchanged
                    if "quantity" in comp and "value" in comp["quantity"]:
                        comp["quantity"]["value"] = int(comp["quantity"]["value"] * percentage)
                    if "totalPrice" in comp:
                        comp["totalPrice"] = comp["totalPrice"] * percentage


def generate_cumulative_daily_files(
    input_file: str,
    output_dir: str,
    service_id: str,
    seed: Optional[int] = None
) -> None:
    """
    Generate cumulative daily usage files from the input JSON file.
    
    Args:
        input_file: Path to the input JSON file
        output_dir: Directory to write output files
        service_id: Service ID to use for all entries
        seed: Optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    # Read input file
    with open(input_file, 'r') as f:
        base_data = json.load(f)
    
    # Parse the period (this is the full month)
    month_start = parse_date(base_data["period"]["from"])
    month_end = parse_date(base_data["period"]["to"])
    
    # Calculate days in the period
    delta = month_end - month_start
    total_days = delta.days
    
    if total_days <= 0:
        raise ValueError("Period must span at least one day")
    
    print(f"Generating {total_days} cumulative daily files from {month_start.date()} to {month_end.date()}")
    print(f"Using service_id: {service_id}")
    print(f"Total monthly amount: {base_data['totalPrice']['value']:.2f} EUR")
    print("-" * 70)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate a file for each day
    for day_idx in range(total_days):
        target_date = month_start + timedelta(days=day_idx)
        
        # Generate cumulative daily usage
        daily_data = generate_cumulative_daily_usage(
            base_data,
            target_date,
            month_start,
            month_end,
            day_idx,
            total_days
        )
        
        # Write to file
        filename = f"usage_{target_date.strftime('%Y-%m-%d')}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(daily_data, f, indent=2)
        
        # Generate SQL insert
        sql_filename = f"insert_{target_date.strftime('%Y-%m-%d')}.sql"
        sql_filepath = output_path / sql_filename
        
        with open(sql_filepath, 'w') as f:
            f.write(generate_sql_insert(daily_data, target_date, service_id))
        
        print(f"Day {day_idx + 1:2d}/{total_days}: {filename} - "
              f"call_timestamp: {target_date.strftime('%Y-%m-%d')}, "
              f"price: {daily_data['totalPrice']['value']:.2f} EUR "
              f"({daily_data['totalPrice']['value'] / base_data['totalPrice']['value'] * 100:.1f}%)")
    
    print("-" * 70)
    print(f"Done! Generated {total_days} cumulative daily files in {output_dir}/")


def generate_sql_insert(data: Dict[str, Any], target_date: datetime, service_id: str) -> str:
    """Generate a SQL INSERT statement for the current_usage_raw table."""
    json_str = json.dumps(data).replace("'", "''")
    
    # Create a datetime with timezone for the call_timestamp
    call_timestamp = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Format without 'Z' at the end for PostgreSQL
    period_from = data["period"]["from"].replace('Z', '+00:00')
    period_to = data["period"]["to"].replace('Z', '+00:00')
    last_update = data["lastUpdate"].replace('Z', '+00:00')
    call_timestamp_str = call_timestamp.isoformat().replace('+00:00', '+00:00')
    
    sql = f"""
-- Insert for {target_date.strftime('%Y-%m-%d')} (cumulative)
-- Total price: {data['totalPrice']['value']:.2f} EUR
-- period_from: {period_from} (full month start)
-- period_to: {period_to} (full month end)
-- call_timestamp: {target_date.strftime('%Y-%m-%d')} (specific day)
INSERT INTO current_usage_raw (
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
    '{call_timestamp_str}',
    '{last_update}',
    {data['totalPrice']['value']:.6f},
    'EUR',
    '{json_str}'::jsonb,
    NOW()
);
"""
    return sql


def main():
    parser = argparse.ArgumentParser(
        description="Generate cumulative daily usage files from a monthly usage JSON"
    )
    parser.add_argument(
        "input_file",
        help="Path to the input JSON file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="./daily_usage",
        help="Output directory for daily files (default: ./daily_usage)"
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
    
    generate_cumulative_daily_files(
        args.input_file,
        args.output_dir,
        args.service_id,
        args.seed
    )


if __name__ == "__main__":
    main()