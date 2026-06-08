# Idaho Child Care Program (ICCP) working references

## Official program name

**Federal Program**: Child Care and Development Fund
**State's Official Name**: Idaho Child Care Program
**Abbreviation**: ICCP
**Variable Prefix**: `id_iccp`
**GitHub issue**: https://github.com/PolicyEngine/policyengine-us/issues/8601

## Downloaded official sources

1. Idaho Department of Health and Welfare, Idaho Child Care Program public page.
   - URL: https://healthandwelfare.idaho.gov/services-programs/children-families-older-adults/idaho-child-care-program
   - Notes: Public-facing program page states the gross monthly income limit is at or below 175% of FPG and links the copay chart.

2. IDAPA 16.06.12, Idaho Child Care Program (current administrative code).
   - URL: https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=7
   - Local file: `/tmp/id-ccap-adminrules.pdf`
   - Notes: Current controlling rules. Section 070 on PDF page 7 sets income limits; Section 105 on PDF page 12 sets eligible child rules; Section 200 on PDF page 13 sets qualifying activities; Sections 502-504 on PDF page 15 set payment and copay rules.

3. Idaho Child Care Copay Chart, effective October 1, 2025.
   - URL: https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=4671&repo=PUBLIC-DOCUMENTS#page=1
   - Local file: `/tmp/id-ccap-copay-chart.pdf`
   - Notes: Effective 2025-10-01. Gives per-child part-time and full-time copays by household size and monthly income, plus student, TAFI, and foster family rows.

4. Idaho Child Care Program Local Market Rates (LMR), effective July 1, 2025.
   - URL: https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=19508&repo=PUBLIC-DOCUMENTS#page=1
   - Local file: `/tmp/id-ccap-local-market-rates.pdf`
   - Notes: Effective 2025-07-01. Gives monthly LMRs by county cluster, age group, provider type, and full-time/part-time activity.

5. Idaho Child Care Program Manual, draft, July 2025.
   - URL: https://publicdocuments.dhw.idaho.gov/WebLink/DocView.aspx?dbid=0&id=34198&repo=PUBLIC-DOCUMENTS#page=6
   - Local file: `/tmp/id-ccap-program-manual-draft.pdf`
   - Notes: Draft manual includes explanations and a conflicting income threshold (130% FPG application, 145% FPG redetermination). Treat as supporting context, not controlling source, unless user decides otherwise.

## Source conflict

The current administrative code and DHW public page use 175% FPG for application/redetermination eligibility. The July 2025 draft manual and October 2025 copay chart use thresholds that align with 130% FPG for the main copay table and 145% FPG redetermination text in the draft manual. Proposed implementation: use current IDAPA/public-page 175% FPG for eligibility and use the 2025 copay chart only to calculate copays for income ranges covered by the chart.

## Existing implementations reviewed

- Rhode Island CCAP: `policyengine_us/variables/gov/states/ri/dhs/ccap`
- Delaware Purchase of Care: `policyengine_us/variables/gov/states/de/dss/poc`
- Connecticut Care 4 Kids: `policyengine_us/variables/gov/states/ct/oec/c4k`
- Arkansas SRA: `policyengine_us/variables/gov/states/ar/ade/oec/sra`

## Major eligibility tests

- Idaho residency/state: model through `defined_for = StateCode.ID`.
- Income at application: countable income cannot exceed 175% FPG under current IDAPA 16.06.12 Section 070.01.
- Continuing eligibility exit: countable income above 85% SMI ends eligibility under Section 070.02.
- Redetermination/graduate phase-out: Section 070.03 uses 175% FPG; exact phase-out duration/benefit reduction is not available from the extracted sources and should be modeled only as an enrolled threshold unless scoped otherwise.
- Eligible child: under age 13, or under age 19 if disabled/incapable of self-care or under supervision order/case plan.
- Citizenship/lawful status: child must be a citizen or lawfully present; noncitizen/non-lawfully-present family members are excluded from family size but their income is counted. PolicyEngine has limited direct variables for lawful presence in this state-program context.
- Qualifying activities: each parent must need care due to employment, self-employment, education/training, preventive services, PRC/negotiated activities; incapacitated-parent exception applies in two-parent families.
- Federal CCDF asset cap should apply via existing `is_ccdf_asset_eligible`.

## Income and deductions

- Count gross earned and unearned income unless excluded.
- Exclude dependent child earnings if the child is under 18 and is not a parent seeking/receiving benefits.
- Exclusions include educational funds, need-specific assistance, nonrecurring lump sums, loans, TAFI, AABD, foster care payments, AmeriCorps/VISTA allowances, income tax refunds/EITC, travel reimbursements, tribal income other than direct wages, adoption assistance, temporary Census income, ORR assistance, and WIA/WIOA benefits.
- Deduct court-ordered child support paid by a parent receiving child care benefits.
- Self-employment has program-specific averaging and 50% standard expense deduction in the draft manual; existing PolicyEngine self-employment variables do not capture the full administrative projection process.

## Benefit calculation

- Per-child maximum equals the lower of provider usual/customary charge and LMR. PolicyEngine can model this as the lower of actual pre-subsidy expenses and LMR-derived maximum.
- LMR chart is monthly by cluster, age group, provider type (center or group/family), and full/part time.
- Final ICCP benefit equals capped allowable cost minus family copay.
- Copay chart is per child by household size and income, with part-time/full-time columns. TAFI and foster families have zero copay; post-secondary student rules require work-hours distinctions.

## Not modeled unless user scopes in with simplification

- Provider licensing/registration/background checks/provider fraud.
- Immunization verification.
- Custody disputes and 51% night rule.
- Exact lawful-presence family-size exclusion and income inclusion for non-counted members.
- Preventive services and PRC activities unless mapped to generic employment/education/work variables.
- Out-of-state provider location rule.
- Redetermination graduated phase-out mechanics beyond an enrolled continuing-income threshold.
