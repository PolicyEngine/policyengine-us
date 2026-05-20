# San Mateo County General Assistance working references

Program: San Mateo County Human Services Agency General Assistance (GA)

Variable prefix: `ca_smc_general_assistance`

Local source copies:
- `/tmp/ca-smc-ga-sources/general_assistance_fact_sheet.pdf`
- `/tmp/ca-smc-ga-sources/standards_of_assistance.pdf`
- `/tmp/ca-smc-ga-sources/nmohc_2026_board_memo.pdf`
- `/tmp/ca-smc-ga-sources/time_limits_2026_resolution.pdf`

Official source URLs:
- General Assistance program page: https://www.smcgov.org/hsa/general-assistance-ga
- Fact sheet PDF, dated 02.2025: https://www.smcgov.org/media/153295/download?inline=#page=1
- Standards of Assistance PDF, C-335 Rev. 12.2025: https://www.smcgov.org/media/156974/download?inline=#page=1
- 2026 NMOHC Board memo, File 26-290, Board date 2026-04-07: https://sanmateocounty.legistar.com/ViewReport.ashx?GID=659&GUID=LATEST&ID=94585&M=R&N=TextL5&Title=Board+Memo#page=1
- 2026 time-limit resolution attachment: https://sanmateocounty.legistar.com/View.ashx?G=1088EC25-A43A-408F-A57C-73C0A70269AB&GUID=7A7BFB1E-AD23-4AC9-A6B2-82EAFFEDABC7&ID=15171150&M=F#page=1

Extracted rules:
- Purpose and administration: County-funded temporary financial support for low-income San Mateo County residents, paid by EBT, direct deposit, or vendor payments for housing/utilities. Source: fact sheet page 1.
- Eligibility factors: age, county residency, identification, Social Security number, citizenship or permanent residency, income, property, employable/unemployable factors, and application for other potential income/resources. Source: fact sheet page 1.
- Immigration: qualified immigrants may be eligible, including lawful permanent residents, refugees, asylum applicants or asylees, conditional entrants, people granted withholding of deportation/removal, and Cuban/Haitian entrants. Source: fact sheet page 1.
- Work requirement: employable recipients must be available for full-time employment and comply with Vocational Rehabilitation Services unless excepted. Examples include full-time employment, required home care for specified relatives, age 65+, school attendance for high-school diploma, child under 16, limited English proficiency, disability, or approved training/rehabilitation. Source: fact sheet page 1.
- Time limits: the February 2025 fact sheet says no time limit if clients follow requirements and remain eligible. A later Board resolution establishes six months of aid in a twelve-month period for employable GA recipients. Sources: fact sheet page 2; time-limit resolution page 1.
- Counted income: earnings, unemployment benefits, disability benefits, self-employment income, retirement benefits, interest income, child or spousal support, and other means of income or support. Source: fact sheet page 2.
- Income test: applicant countable income is compared with the GA payment standard based on living arrangement. Source: fact sheet page 2.
- Maximum aid payments in current public chart: independent living $732, drug and alcohol treatment center $732, NMOHC without BHRS/SMMC referral $732, NMOHC with BHRS/SMMC referral $1,599.07. Source: standards PDF page 1.
- NMOHC update: Board File 26-290 recommends and documents an increase for SSI-pending NMOHC facility GA recipients with BHRS/SMMC referral from $1,599.07 to $1,626.07 effective 2026-01-01. Source: NMOHC Board memo pages 1-2.
- Property: property such as cash, bank accounts, or a vehicle is considered; property must be under $1,464; one vehicle regardless of value is exempt. Sources: fact sheet page 2; standards PDF page 1.
- Other programs: enrollment in CalFresh, Medi-Cal, or SSI does not automatically preclude GA; the fact sheet says the family may also qualify. Source: fact sheet page 2.
- Verification, interview, QR7, annual renewal, reporting changes within 10 days, application methods, and application processing within 30 days are administrative rules. Source: fact sheet pages 2-3.
- Ordinance authority: the Board memo cites California law requiring counties to support indigent residents who do not qualify for other financial assistance and San Mateo County Ordinance Code Section 2.30.050 as assigning HSA responsibility for GA rules and regulations. Source: NMOHC Board memo page 1.

Data notes:
- The Standards of Assistance PDF contains scanned/image content; `pdftotext` returned no text. A 300 DPI render was saved as `/tmp/ca-smc-ga-sources/standards_of_assistance-1.png` and visually inspected.
- Every PDF citation above includes `#page=1` or `#page=2`.

Potential modeling constraints:
- PolicyEngine does not generally know whether a person completed county work activity assignments, has applied for all alternative income, satisfies reporting/verification duties, or has exhausted an employable-recipient time limit.
- Living arrangement and BHRS/SMMC referral status are not standard household variables; modeling all payment standards likely requires new input variables.
- Current public sources list countable income categories but do not give a full GA income disregard schedule beyond broad category examples.
