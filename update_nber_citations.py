#!/usr/bin/env python3

# Generate NBER citations for all years
years_1990_2008 = list(range(1990, 2009))
years_2020_2025 = list(range(2020, 2026))
all_years = years_2020_2025[::-1] + years_1990_2008[::-1]  # Reverse order

def generate_line_8_citations():
    """Generate citations for Line 8 - Additional Exemptions"""
    citations = []
    
    # 2020-2025
    for year in years_2020_2025[::-1]:
        citations.append(f"""    - title: {year} New Hampshire DP-10 Form (Line 8 - Additional Exemptions)
      href: https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/dp-10-{year}{"" if year > 2020 else "-print"}.pdf#page=3""")
    
    # 1990-2008  
    for year in years_1990_2008[::-1]:
        page = 3 if year >= 1995 else 2
        citations.append(f"""    - title: {year} New Hampshire DP-10 Form (Line 8 - Additional Exemptions)
      href: https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/dp-10-{year}.pdf#page={page}""")
    
    return "\n".join(citations)

def generate_line_10_citations():
    """Generate citations for Line 10 - Tax Rate"""
    citations = []
    
    # 2020-2025
    for year in years_2020_2025[::-1]:
        citations.append(f"""    - title: {year} New Hampshire DP-10 Form (Line 10 - Tax Rate)
      href: https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/dp-10-{year}{"" if year > 2020 else "-print"}.pdf#page=4""")
    
    # 1990-2008
    for year in years_1990_2008[::-1]:
        page = 4 if year >= 1995 else 3
        citations.append(f"""    - title: {year} New Hampshire DP-10 Form (Line 10 - Tax Rate)
      href: https://taxsim.nber.org/historical_state_tax_forms/NH/{year}/dp-10-{year}.pdf#page={page}""")
    
    return "\n".join(citations)

print("Line 8 Citations (for old_age_addition, blind_addition, disabled_addition):")
print("="*80)
print(generate_line_8_citations())
print("\n\nLine 10 Citations (for rate.yaml):")
print("="*80)
print(generate_line_10_citations())