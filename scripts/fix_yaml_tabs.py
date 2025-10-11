#!/usr/bin/env python
"""Fix YAML files that contain tabs by replacing them with spaces."""

import os
from pathlib import Path
import sys

def fix_yaml_tabs(directory):
    """Replace tabs with spaces in YAML files."""
    yaml_files = Path(directory).rglob("*.yaml")
    fixed_count = 0
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '\t' in content:
                # Replace tabs with 4 spaces
                fixed_content = content.replace('\t', '    ')
                
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"Fixed tabs in: {yaml_file}")
                fixed_count += 1
                
        except Exception as e:
            print(f"Error processing {yaml_file}: {e}")
    
    print(f"\nFixed {fixed_count} files with tabs")

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else "policyengine_us/parameters"
    fix_yaml_tabs(directory)