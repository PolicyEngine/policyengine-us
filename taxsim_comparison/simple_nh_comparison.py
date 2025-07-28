#!/usr/bin/env python3
"""Simple comparison of PolicyEngine NH tax calculations with TAXSIM results."""

import pandas as pd

# Read TAXSIM results
taxsim_df = pd.read_csv('taxsim_results.csv', skiprows=[0, 9, 10, 11, 12, 13, 14, 15, 16])
taxsim_df.columns = taxsim_df.columns.str.strip()

print("TAXSIM Results Summary:")
print("v30 = NH interest+dividend income")
print("v34 = NH exemptions") 
print("v36 = NH taxable income")
print("siitax = NH tax")
print()

# Show TAXSIM results
taxsim_summary = taxsim_df[['taxsimid', 'year', 'siitax', 'v30', 'v34', 'v36']].head(7)
taxsim_summary.columns = ['ID', 'Year', 'Tax', 'Income', 'Exemptions', 'Taxable']
print(taxsim_summary.round(2))

# PolicyEngine expected results based on our implementation
pe_results = []

# Test Case 1: 2020, Single, $10k income (5k int + 5k div)
# Exemptions: $2,400 base
# Taxable: $10,000 - $2,400 = $7,600
# Tax: $7,600 * 0.05 = $380
pe_results.append({'ID': 1, 'Year': 2020, 'Status': 'Single', 
                   'PE_Income': 10000, 'PE_Exemptions': 2400, 
                   'PE_Taxable': 7600, 'PE_Tax': 380})

# Test Case 2: 2020, Joint, $5k income
# Exemptions: $4,800 base  
# Taxable: $5,000 - $4,800 = $200
# Tax: $200 * 0.05 = $10
pe_results.append({'ID': 2, 'Year': 2020, 'Status': 'Joint',
                   'PE_Income': 5000, 'PE_Exemptions': 4800,
                   'PE_Taxable': 200, 'PE_Tax': 10})

# Test Case 3: 2020, Single, $20k income
# Exemptions: $2,400 base
# Taxable: $20,000 - $2,400 = $17,600  
# Tax: $17,600 * 0.05 = $880
pe_results.append({'ID': 3, 'Year': 2020, 'Status': 'Single',
                   'PE_Income': 20000, 'PE_Exemptions': 2400,
                   'PE_Taxable': 17600, 'PE_Tax': 880})

# Test Case 4: 1990, Single, $10k income
# Exemptions: $1,200 base
# Taxable: $10,000 - $1,200 = $8,800
# Tax: $8,800 * 0.05 = $440  
pe_results.append({'ID': 4, 'Year': 1990, 'Status': 'Single',
                   'PE_Income': 10000, 'PE_Exemptions': 1200,
                   'PE_Taxable': 8800, 'PE_Tax': 440})

# Test Case 5: 1990, Joint, $5k income
# Exemptions: $2,400 base
# Taxable: $5,000 - $2,400 = $2,600
# Tax: $2,600 * 0.05 = $130
pe_results.append({'ID': 5, 'Year': 1990, 'Status': 'Joint',
                   'PE_Income': 5000, 'PE_Exemptions': 2400,
                   'PE_Taxable': 2600, 'PE_Tax': 130})

# Test Case 6: 1980, Single, $10k income  
# Exemptions: $600 base
# Taxable: $10,000 - $600 = $9,400
# Tax: $9,400 * 0.05 = $470
pe_results.append({'ID': 6, 'Year': 1980, 'Status': 'Single',
                   'PE_Income': 10000, 'PE_Exemptions': 600,
                   'PE_Taxable': 9400, 'PE_Tax': 470})

# Test Case 7: 1980, Joint, $5k income
# Exemptions: $1,200 base
# Taxable: $5,000 - $1,200 = $3,800
# Tax: $3,800 * 0.05 = $190
pe_results.append({'ID': 7, 'Year': 1980, 'Status': 'Joint',
                   'PE_Income': 5000, 'PE_Exemptions': 1200,
                   'PE_Taxable': 3800, 'PE_Tax': 190})

pe_df = pd.DataFrame(pe_results)

print("\n\nPolicyEngine Expected Results:")
print(pe_df)

print("\n\nComparison:")
print("-" * 80)
print(f"{'ID':>3} {'Year':>6} {'Status':>8} | {'TAXSIM Tax':>11} {'PE Tax':>11} {'Diff':>11} | Note")
print("-" * 80)

for i in range(7):
    taxsim_row = taxsim_df.iloc[i]
    pe_row = pe_df.iloc[i]
    
    tax_diff = taxsim_row['siitax'] - pe_row['PE_Tax']
    
    # Check exemptions difference
    exemp_diff = taxsim_row['v34'] - pe_row['PE_Exemptions']
    
    note = ""
    if abs(tax_diff) > 0.01:
        if abs(exemp_diff) > 1:
            note = f"Exemption diff: TAXSIM ${taxsim_row['v34']:.0f} vs PE ${pe_row['PE_Exemptions']:.0f}"
        else:
            note = f"Taxable diff: TAXSIM ${taxsim_row['v36']:.0f} vs PE ${pe_row['PE_Taxable']:.0f}"
    else:
        note = "Match!"
    
    print(f"{pe_row['ID']:3d} {pe_row['Year']:6d} {pe_row['Status']:>8} | "
          f"${taxsim_row['siitax']:10.2f} ${pe_row['PE_Tax']:10.2f} ${tax_diff:10.2f} | {note}")

print("\n\nKey Findings:")
print("1. TAXSIM uses higher exemptions than we expected based on the forms")
print("2. The differences are systematic - TAXSIM's exemptions appear to include additional amounts")
print("3. Need to investigate why TAXSIM exemptions differ from the base amounts in tax forms")