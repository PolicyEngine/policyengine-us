# HUD Section 8 Income Limits

`section8_income_limits.csv` contains HUD FY2024 and FY2025 Section 8
income limits from HUD's Income Limits datasets:

https://www.huduser.gov/portal/datasets/il.html

The original HUD files include subcounty rows for some areas. PolicyEngine
currently stores county FIPS on households, so duplicate county-year rows are
collapsed to the median numeric value for that county-year. Direct county rows
therefore pass through unchanged, and subcounty-only counties use a lossy
county-level fallback, matching the Fair Market Rent lookup pattern.
