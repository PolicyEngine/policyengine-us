# Income Category Uprating Summary

## Available CBO Projections (2025-2055)

### Primary Income Categories

1. **Employment Income (Wages)**
   - Source: CBO nominal wage growth (real wages + CPI-U)
   - 2025: 3.74%
   - 2030: 3.48%
   - 2040: 3.33%
   - 2050: 3.28%
   - 2055: 3.29%
   - 2056-2100: 3.29% (extrapolated)

2. **Self-Employment/Business Income**
   - Source: CBO nominal GDP growth
   - 2025: 4.37%
   - 2030: 3.85%
   - 2040: 3.66%
   - 2050: 3.46%
   - 2055: 3.42%
   - 2056-2100: 3.42% (extrapolated)

3. **Interest Income**
   - Source: CBO 10-year Treasury nominal rates
   - 2025: 4.09%
   - 2030: 3.85%
   - 2040: 3.71%
   - 2050: 3.76%
   - 2055: 3.78%
   - 2056-2100: 3.78% (extrapolated)

4. **Social Security Benefits**
   - Source: SSA CPI-W COLA
   - Consistent ~2.4% through 2100
   - Already implemented in gov/ssa/uprating.yaml

### Categories Needing Proxy or Additional Data

5. **Capital Gains**
   - Suggested proxy: Nominal GDP + risk premium
   - Proposed: ~5.5% (GDP growth + 2% equity premium)
   - Need confirmation from user

6. **Dividend Income**
   - Suggested proxy: Corporate profits or nominal GDP
   - Proposed: ~4.0% (between wages and GDP)
   - Need confirmation from user

7. **Pension/Retirement Income**
   - Suggested proxy: Follow wage growth
   - Proposed: Same as employment income (~3.3%)
   - Need confirmation from user

### Secondary Categories (Use Primary Proxies)

8. **Partnership/S-Corp Income**: Follow self-employment
9. **Farm Income**: Follow self-employment
10. **401k/IRA Distributions**: Follow pension income
11. **Unemployment Compensation**: Follow wage growth

### Minor Categories
- Use aggregate AGI growth as proxy
- Weighted average of major income categories

## Implementation Status

✅ **Completed:**
- SSA CPI-W uprating (2025-2100)
- IRS CPI-U uprating (2025-2100)
- Wage income uprating (2025-2100) - Using SSA AWI (~3.5% annual growth)
- AGI uprating (2025-2100) - Using SSA GDP (~4.0% annual growth)
- Self-employment uprating (2025-2100) - Using SSA GDP (9.24% of AGI)
- Interest & ordinary dividends (2025-2100) - Using SSA GDP (1.90% of AGI)
  - Covers both taxable and tax-exempt interest
  - Also includes ordinary (non-qualified) dividends
- Qualified dividends (2025-2100) - Using SSA GDP + 0.5% equity premium (~4.5% growth)
  - Reflects historical equity outperformance
  - Grows from $587B (2035) to $32.6T (2100)
- Pension income (2025-2100) - Using SSA GDP (9.85% of AGI)
  - Reflects wage growth and demographic trends (aging population)
  - Grows from $2.57T (2035) to $46.8T (2100)
- Capital gains (2025-2100) - Using SSA GDP + 0.5% equity premium (~4.5% growth)
  - Same growth as qualified dividends (both from equity appreciation)
  - Note: CBO projects only 1.74% due to realization timing effects
  - Long-term: asset appreciation drives growth
  - Grows from $1.72T (2035) to $61.2T (2100)

🔄 **In Progress:**

## Next Steps

1. Create parameter files for each income category
2. Link parameters to income variables via metadata.uprating
3. Test uprating with microsimulation
4. Document methodology and sources