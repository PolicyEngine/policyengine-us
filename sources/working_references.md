# Orange County General Relief working references

## Program

- Program: Orange County, California General Relief (GR).
- Variable prefix: `ca_oc_general_relief`.
- Parameter prefix: `gov.local.ca.oc.general_relief`.
- Registry status: `partial`.
- Official regulations index: https://www.ssa.ocgov.com/page/general-relief-regulations
- Official FAQ: https://www.ssa.ocgov.com/cash-calfresh/faqs/general-relief
- User-provided consolidated manual: `/Users/ziminghua/Downloads/GR Regulation Manual.pdf`
- Consolidated manual SHA-256: `2a9f4e5be086106b73f6b22abb55127461bdec873164b0671e81fc42b8bb47d7`
- Consolidated manual metadata: Orange County Social Services Agency, created March 19, 2026, 58 PDF pages.
- Extraction: `/tmp/ca-oc-general-relief-docs/manual-text/gr-regulation-manual.txt`
- Rendered pages: `/tmp/ca-oc-general-relief-docs/manual-rendered/page-01.png` through `page-58.png`

## Official PDF references

- Section 10, Introduction:
  https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2010%20-%20Approved%20-%20January%202026.pdf#page=01
- Section 20, Eligibility Determination:
  https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2020%20-%20Approved%20-%20January%202026.pdf#page=01
- Section 30, Program Requirements and Penalties:
  https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2030%20-%20Approved%20-%20January%202026.pdf#page=01
- Section 40, Residence:
  https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2040%20-%20Approved%20-%20January%202026.pdf#page=01
- Section 50, Real Property:
  https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2050%20-%20Approved%20-%20March%202023_0.pdf#page=01
- Section 60, Personal Property:
  https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=01
- Section 70, Income:
  https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Income.pdf#page=01
- Section 80, Benefits and Services:
  https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=01
- Section 90, Responsible Relatives:
  https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2090%20-%20Approved%20-%20March%202023_0.pdf#page=01

## Verified simulatable rules

- GR is a residual relief program for people ineligible for federal or state cash aid programs. Section 10.3, PDF page 01.
- A GR economic unit (GR-EU) includes people living together who are legally and/or economically dependent. Section 10.6.j, PDF page 05.
- The FAQ describes the target population as eligible indigent adult lawful residents without custody of minor children.
- Recipients of SSI/SSP, CalWORKs, and Refugee Cash Assistance are excluded members of the GR-EU. Section 20.4.b, PDF page 03.
- County residence requires 15 consecutive calendar days immediately before application. Section 40.2, PDF page 01.
- Eligible immigration pathways include U.S. citizens, permanent legal residents, people granted an indefinite stay from deportation, and qualifying victims of trafficking, domestic violence, and other serious crimes. Temporary visa holders and undocumented non-citizens are ineligible. Section 40.1, PDF page 01.
- Primary-residence real property is limited to $5,000 net value. Combined countable secondary real and personal property is limited to $1,000. Section 50.2, PDF page 01.
- Cash or liquid resources over $50 reduce the initial-month grant. Section 60.2.a, PDF page 01.
- Personal-property exclusions include household furniture and personal effects up to $500, one vehicle per EU with net value up to $4,650, and qualifying burial reserves up to $1,000. Section 60.4, PDF page 02.
- Current income includes earned income, countable grants or gifts, certain loans, rental income, lump sums, retirement withdrawals, and 10% of roomer or boarder payments. Energy assistance and qualifying reimbursements are excluded. Section 70.2, PDF pages 01-03.
- Net earned income deducts 20% of gross earnings, medical insurance payments, and verified court-ordered support actually paid. Section 70.2.o, PDF page 04.
- Net unearned income deducts medical insurance payments, verified court-ordered support actually paid, and mandatory federal or state income tax deductions. Section 70.2.p, PDF page 04.
- Financial eligibility subtracts current net income from the maximum aid payment (MAP). Section 80.2.d, PDF page 02.
- MAP excludes children and other excluded members. Section 80.2.d, PDF page 02.
- CalWORKs or RCA recipient members use a difference-of-MAP method; other excluded members use the MAP for eligible GR-EU members. Section 80.3.a, PDF page 04.
- Shared housing reduces MAP by 15% for one unrelated person, 20% for two unrelated people, and 25% for three or more unrelated people. Section 80.3.a.3, PDF page 04.
- Housing and utility expenses are allowed up to the housing and utility component value. Homeless people receive the full housing and utility component value. Section 80.3.b.1, PDF page 05.
- Food, transportation, and clothing component values are deducted only when the entire component is provided at no cost. CalFresh receipt does not reduce the food component value. Section 80.3.b.1, PDF page 05.
- Employable participants are limited to 90 days of GR benefits in any 12-month period. Section 30.7.c, PDF page 05.

## Important missing source

The official regulations define the regular monthly benefit formula but do not publish:

- the regular MAP table by eligible GR-EU size;
- the housing and utility component values;
- the food component values;
- the transportation component values;
- the clothing component values.

These values are required to calculate the ordinary monthly GR benefit. Request an official Orange County companion schedule, procedure, or current eligibility handbook before implementing the full payment calculation.
