#!/usr/bin/env python3
import subprocess
import os

# Based on our check, only these forms actually exist
existing_forms = [
    (2020, "dp-10-2020-print.pdf"),
    (2021, "dp-10-2021-print.pdf"),
    (2022, "dp-10-2022-print.pdf")
]

print("Downloading and verifying NBER forms...")
print("=" * 60)

# Create temp directory for downloads
os.makedirs("temp_forms", exist_ok=True)

for year, filename in existing_forms:
    url = f"https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/{filename}"
    local_path = f"temp_forms/{filename}"
    
    print(f"\nDownloading {year} form...")
    result = subprocess.run(['curl', '-o', local_path, url], capture_output=True)
    
    if result.returncode == 0 and os.path.exists(local_path):
        print(f"✓ Downloaded {filename}")
        # Now I'll read each one to verify page numbers
    else:
        print(f"✗ Failed to download {filename}")

print("\nPlease read each form to verify:")
print("- Line 6 (Base Exemptions) - expected on page 2")  
print("- Line 8 (Additional Exemptions) - expected on page 2-3")
print("- Line 10 (Tax Rate) - expected on page 3-4")