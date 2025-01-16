import csv
import re
from pathlib import Path
import logging
from typing import Dict, Tuple, List

print("Script starting...")

def extract_county_mappings(enum_file: str) -> Dict[str, str]:
    """
    Extract county mappings from the PolicyEngine US County enum file.
    Returns a dict mapping formatted name (e.g., "Aleutians East Borough, AK") 
    to enum name (e.g., "ALEUTIANS_EAST_BOROUGH_AK")
    """
    print(f"Reading county mappings from {enum_file}")
    mappings = {}
    with open(enum_file, 'r') as f:
        for line in f:
            if '=' in line and '"' in line and 'class' not in line:
                try:
                    key, value = line.strip().split('=', 1)
                    enum_name = key.strip()
                    formatted_name = value.strip().strip('"').strip("'").strip()
                    if enum_name != "UNKNOWN":
                        # Store mapping from formatted to enum name
                        mappings[formatted_name] = enum_name
                        print(f"Found mapping: {formatted_name} -> {enum_name}")
                except ValueError as e:
                    print(f"Skipping invalid mapping line: {line}. Error: {e}")
    return mappings

def standardize_county_name(name: str, state: str) -> str:
    """
    Standardize a county name for matching.
    """
    # Convert to uppercase and remove any dots
    name = name.upper().replace('.', '')
    
    # Remove common suffixes and standardize spaces/special characters
    name = re.sub(r'\s+COUNTY$|\s+PARISH$|\s+BOROUGH$|\s+CENSUS\s+AREA$|\s+MUNICIPALITY$', '', name)
    name = re.sub(r'[,\s]+', '_', name.strip())
    name = re.sub(r'[^A-Z0-9_]', '', name)
    
    # Remove consecutive underscores and trailing underscores
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    
    # Add state suffix
    return f"{name}_{state}"

def process_counties(ratings_csv: str, enum_file: str, output_dir: str):
    """
    Process county data and create standardized output.
    """
    print(f"\nProcessing counties...")
    print(f"Ratings CSV: {ratings_csv}")
    print(f"Enum file: {enum_file}")
    print(f"Output directory: {output_dir}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load mappings (formatted name -> enum name)
    mappings = extract_county_mappings(enum_file)
    print(f"Loaded {len(mappings)} county mappings")
    
    # Create reverse mappings for standardized matching
    std_mappings = {}
    for formatted_name, enum_name in mappings.items():
        state = formatted_name[-2:]  # Get state from end of formatted name
        county = formatted_name[:-4]  # Remove ", XX" from end
        std_name = standardize_county_name(county, state)
        std_mappings[std_name] = enum_name
    
    # Process ratings CSV
    output_rows = []
    unmatched = set()
    total_processed = 0
    
    print("Reading ratings CSV...")
    with open(ratings_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_processed += 1
            if total_processed % 100 == 0:
                print(f"Processed {total_processed} rows...")
                
            try:
                county = row['county_standardized']
                state = row['state']
                rating_area = str(int(float(row['rating_area'])))  # Remove .0
                
                # Try to find matching enum name
                std_name = standardize_county_name(county, state)
                if std_name in std_mappings:
                    enum_name = std_mappings[std_name]
                    output_rows.append({'county': enum_name, 'rating_area': rating_area})
                else:
                    unmatched.add(f"{county}, {state}")
                    # For unmatched, create an enum-style name
                    enum_style = standardize_county_name(county, state)
                    output_rows.append({'county': enum_style, 'rating_area': rating_area})
                    
            except Exception as e:
                print(f"Error processing row: {row}. Error: {e}")
    
    # Save output
    output_path = output_dir / 'county_rating_areas.csv'
    print(f"\nWriting output to {output_path}")
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['county', 'rating_area'])
        writer.writeheader()
        writer.writerows(output_rows)
    
    # Write unmatched counties
    if unmatched:
        unmatched_path = output_dir / 'unmatched_counties.txt'
        print(f"Writing {len(unmatched)} unmatched counties to {unmatched_path}")
        with open(unmatched_path, 'w') as f:
            f.write('\n'.join(sorted(unmatched)))
    
    print(f"\nProcessing complete!")
    print(f"Total counties processed: {total_processed}")
    print(f"Successfully matched: {total_processed - len(unmatched)}")
    print(f"Unmatched counties: {len(unmatched)}")

def main():
    print("Starting main function...")
    
    # Configure paths based on PolicyEngine US structure
    script_path = Path(__file__).resolve()
    print(f"Script path: {script_path}")
    
    base_path = script_path.parents[7]  # Go up 7 levels to reach policyengine_us root
    print(f"Base path: {base_path}")
    
    enum_file = base_path / 'policyengine_us/variables/household/demographic/geographic/county/county_enum.py'
    ratings_csv = base_path / 'policyengine_us/parameters/gov/aca/county_ratings.csv'
    output_dir = base_path / 'policyengine_us/parameters/gov/hhs/medicaid/geography/standard_county_names'
    
    print(f"Checking if enum file exists: {enum_file.exists()}")
    print(f"Checking if ratings csv exists: {ratings_csv.exists()}")
    
    try:
        process_counties(
            str(ratings_csv),
            str(enum_file),
            str(output_dir)
        )
    except Exception as e:
        print(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    print("Script starting...")
    main()