# Kansas LIEAP regular heating assistance

Coverage is partial for the FY2025 and FY2026 heating seasons. Cooling, crisis,
weatherization, and equipment assistance are outside this implementation.

## Rules and authorities

| Component | Authority | Implementation |
| --- | --- | --- |
| Kansas residence, household membership and qualified members | KEESM 13310-13330 | Kansas SPM units; qualified members determine size, all members' countable income enters the income test. |
| Heating cost responsibility | KEESM 13340 | Separately purchased heat or heat included in unsubsidized rent; a direct input handles exceptional housing/debt arrangements. |
| Income test and reuse of verified income | KEESM 13360 | Every household must meet the income limit; SNAP, TANF or SSI receipt does not waive the total-income test. |
| Self-employment | KEESM 13360 | Gross receipts less 25%, or higher allowable actual costs, when gross receipts are supplied. |
| Child earnings, interest and other income | KEESM 13360-13361 | Exclude earnings and interest of children under 18; count modeled income sources subject to the documented limitations below. |
| Income limits | KEESM 13362 | Published monthly tables, annualized; do not substitute unrounded 150% FPG calculations. |
| Benefit amount | KEESM 13410; annual benefit matrices | Fuel, monthly income band, utility rate tier, dwelling type and eligible household size group. |
| Minimum payment | FY2025/FY2026 state plans, section 2.6 | $100/$130 respectively. |

Historical manual editions:

- [October 2024 eligibility](https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13300.htm)
- [October 2024 income rules and limits](https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm)
- [January 2026 eligibility](https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13300.htm)
- [January 2026 income rules and limits](https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm)
- [Benefit rules](https://content.dcf.ks.gov/ees/keesm/current/keesm13400.htm)

Benefit sources:

- [FY2025 state plan, section 2](https://liheapch.acf.gov/docs/2025/state-plans/KS_Plan_2025.pdf#page=8)
- [FY2026 state plan, section 2](https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8)
- [FY2025 matrix, 100% values](https://liheapch.acf.gov/docs/2025/benefits-matricies/KS_BenefitMatrix_2025.pdf)
- [FY2026 matrix, adjusted 80% values](https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf)

All 1,984 encoded cells were compared with the official PDFs on September 28,
2026. The matrix maxima are $2,232 and $1,682 respectively. The plans' maximum
benefits do not reduce any cell, so an extra maximum cap cannot bind.

## Source reconciliation

The state plan's categorical-eligibility wording describes reuse of verified
income. KEESM 13360 explicitly still tests the combined household income. The
plan's unchecked combined interest/dividends/royalties box is not treated as a
blanket exclusion: KEESM 13361 specifies the exemptions. The October 2024
LIEAP-specific text exempts interest and dividends up to $50 monthly, counting
the full amount above that threshold. The January 2026 text instead exempts
small irregular, unpredictable payments, not regular interest generally.
The model follows each season's LIEAP-specific manual; the FY2026 irregular
payment exception requires a direct countable-income input.

There is no modeled household contribution requirement. DCF eliminated the
former self-payment rule in [revision 114, effective February 2024](https://content.dcf.ks.gov/EES/KEESM/SOC_Rev_114_02_24.html).

## Periods and modeling limitations

- A YEAR calculation for 2025 or 2026 selects that year's heating season.
  October parameter dates index the federal fiscal-year schedules. They do not
  represent application opening dates. Income divided by twelve approximates
  the application month; callers can supply annualized application-month
  countable income directly. Weekly/biweekly conversions and irregular receipt
  timing are not inferred from annual data.
- The SPM unit approximates the energy household. Shared addresses, paid
  attendants, college dormitories, duplicate state/tribal awards, and application
  administration are not independently resolved.
- Tier E and house/modular/mobile are modeling defaults, not legal findings
  about a household. Supply the actual vendor tier and dwelling type. Solar
  heat follows the shared grid-tied electric-heat convention.
- Supply `ks_liheap_energy_vulnerable` for shared unmetered heat, qualifying
  prior-address heating debt, excess subsidized-housing charges, or limited FHA
  assistance. A fuel type alone does not establish purchased heating costs.
- Self-employment receipts default to -1 (unknown). Without gross receipts,
  positive reported net business/farm income is a fallback; it receives no
  second expense deduction. Actual allowable costs and the standard deduction
  require the gross-receipts input.
- Source-specific exemptions and missing receipt types, including irregular
  interest, burial-fund interest, some cash gifts, contract payments, royalties,
  settlements and foster/adoption payments, are not fully distinguished by
  available inputs. Use directly supplied countable income for such cases.
  Coverage remains partial rather than implying those amounts are all exempt.
