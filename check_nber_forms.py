#!/usr/bin/env python3
import subprocess
import sys

def check_url(url):
    """Check if a URL exists by getting HTTP headers"""
    result = subprocess.run(['curl', '-I', '-s', url], capture_output=True, text=True)
    return '200 OK' in result.stdout

# Years to check
years_to_check = list(range(1990, 2009)) + list(range(2020, 2026))

print("Checking which NH DP-10 forms exist on NBER...")
print("=" * 60)

existing_forms = []

for year in years_to_check:
    base_url = f"https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/"
    
    # Try different filename patterns
    patterns = [
        f"dp-10-{year}.pdf",
        f"dp-10-{year}-print.pdf",
        f"DP-10-{year}.pdf",
        f"DP-10-{year}-print.pdf"
    ]
    
    found = False
    for pattern in patterns:
        url = base_url + pattern
        if check_url(url):
            print(f"✓ {year}: {pattern}")
            existing_forms.append((year, pattern))
            found = True
            break
    
    if not found:
        print(f"✗ {year}: No form found")

print("\nSummary:")
print(f"Found {len(existing_forms)} forms out of {len(years_to_check)} years checked")