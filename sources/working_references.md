# Mississippi Working Disabled Medicaid Buy-In References

## Official Program Name

**Federal Program**: Medicaid Buy-In for workers with disabilities
**State's Official Name**: Working Disabled
**Abbreviation**: WD
**Source**: Mississippi Division of Medicaid, Working Disabled page
**Variable Prefix**: `ms_wd`

## Official Sources

1. Mississippi Division of Medicaid, Working Disabled
   - https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/
   - Confirms WD is a Buy-In program; 40 hours/month paid work; Social Security disability definition without SGA; 250% FPL earnings limit; 135% FPL unearned income limit; $24,000 individual and $26,000 couple resource limits; premium above 150% FPL equal to 5% of countable earnings.

2. Mississippi Division of Medicaid, Medicaid Eligibility Guide for Persons Working and Disabled
   - https://www.medicaid.ms.gov/wp-content/uploads/2014/03/Working-Disabled.pdf#page=1
   - Public guide restating program purpose, 40 hours/month paid work, disability without SGA, separate earned/unearned income tests, and resource exclusions.

3. Mississippi Division of Medicaid, Eligibility Policy and Procedures Manual, Chapter 400, section 400.06 Working Disabled COE-025
   - https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=30
   - Establishes July 1, 1999 implementation and work/disability requirements.
   - https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=31
   - Establishes $24,000/$26,000 resource limits and SSI-based disability treatment.
   - https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32
   - Establishes marital-unit earned and unearned income budgeting, 250% FPL earned test, 135% FPL unearned test, $50 unearned exclusion, 150% FPL premium trigger, and 5% premium.

4. Mississippi Division of Medicaid, Administrative Code Part 104 Income
   - https://www.medicaid.ms.gov/wp-content/uploads/2014/01/Admin-Code-Part-104.pdf#page=23
   - Lists the earned-income exclusion order, including remaining general exclusion, $65 earned exclusion, and one-half remainder exclusion.
   - https://www.medicaid.ms.gov/wp-content/uploads/2014/01/Admin-Code-Part-104.pdf#page=24
   - Describes the $65 plus one-half earned income exclusion.

5. Mississippi Division of Medicaid, Appendix A-5 Sliding Scale for Working Disabled Premiums, revised March 1, 2026
   - https://medicaid.ms.gov/wp-content/uploads/2026/03/Appendix-A-5-WD-Premiums-for-March-2026.pdf#page=1
   - Shows 2026 individual/couple premium table.
   - https://medicaid.ms.gov/wp-content/uploads/2026/03/Appendix-A-5-WD-Premiums-for-March-2026.pdf#page=3
   - States premiums apply for countable earned income between 150% and 250% FPL and equal 5% of countable earnings.

## Source Collection Notes

Downloaded PDFs, extracted text, and 300-DPI page renders are stored under `/tmp/ms-working-disabled-medicaid-buy-in-sources/`.

## Main Requirements

- Disabled individual must work at least 40 hours/month in paid activity.
- Disability follows SSI/Social Security criteria except SGA and current work are ignored.
- Each spouse applying as WD must be disabled and must meet the work test.
- Budget unit is the individual or marital unit, including an ineligible spouse.
- Countable earned income from applicant and spouse must not exceed 250% FPL for individual/couple.
- Countable unearned income from applicant and spouse, after the $50 general exclusion, must not exceed 135% FPL for individual/couple.
- Countable resources must not exceed $24,000 for an individual or $26,000 for a couple.
- Countable earned income above 150% FPL triggers a monthly premium; the premium is 5% of countable earned income.

## Not Modeled

- Regional office application, DDS referral, notices, invoices, retroactive eligibility, and premium payment enforcement.
- Allocations to ineligible children.
- Student earned income, impairment-related work expenses, blind work expenses, PASS, and infrequent/irregular income exclusions.
- Mississippi-specific second-vehicle, income-producing property, personal-property, and life-insurance resource exclusions beyond existing `ssi_countable_resources` inputs.

# Healthier Mississippi Waiver Working References

## Official Program Name

**Federal Program**: Medicaid section 1115 demonstration
**State's Official Name**: Healthier Mississippi Waiver
**Abbreviation**: HMW
**Source**: Mississippi Division of Medicaid, Healthier Mississippi Waiver page
**Variable Prefix**: `ms_hmw`

## Official Sources

1. Mississippi Division of Medicaid, Healthier Mississippi Waiver page.
   - URL: https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/healthier-mississippi-waiver/
   - Key points: enrollment began January 1, 2006; cap is 6,000; eligibility includes age 65 or older or disabled under SSI rules, no Medicare, not pregnant; income no more than 135% FPL; resources below $4,000 individual / $6,000 couple; excluded benefits include long-term care, swing bed, and maternity/newborn care.

2. Mississippi Division of Medicaid, Healthier Mississippi Waiver Fact Sheet 2026.
   - URL: https://medicaid.ms.gov/wp-content/uploads/2026/02/HMW-Fact-Sheet-2026.pdf#page=1
   - Relevant pages:
     - #page=1: enrollment start date, cap, Medicare exclusion, age/disability/pregnancy rules, 135% FPL rule, resource exclusions and countable resources.
     - #page=2: 2026 monthly income examples, couple income rule, covered service exclusions, application instructions.

3. Centers for Medicare & Medicaid Services / Mississippi Division of Medicaid, Healthier Mississippi Extension, approved September 24, 2024.
   - URL: https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=1
   - Relevant pages:
     - #page=1: expenditure authority for aged, blind, or disabled individuals at or below 135% FPL, not Medicare-eligible, and not otherwise Medicaid state plan eligible.
     - #page=3: demonstration history and extension through September 30, 2029 with no programmatic changes.
     - #page=9: eligibility rule, SSI-based income methodology, $4,000/$6,000 resource limits, enrollment cap, and benefit exclusions.

4. Mississippi Division of Medicaid, Member Coverage Descriptions Job Aid, April 3, 2024.
   - URL: https://medicaid.ms.gov/wp-content/uploads/2024/04/20240403_MES_Gainwell_PRP-101_Member-Coverage-Description-Job_Aid_v0.1.pdf#page=5
   - Relevant pages:
     - #page=5: COE 045, "PLAD Healthier MS Waiver - no Medicare"; income up to 135% of poverty; aged or disabled; not eligible for Medicare; $4,000/$6,000 resource test; benefit exclusions.

5. Mississippi Division of Medicaid, Healthier Mississippi Waiver Full Public Notice, July 19, 2022.
   - URL: https://medicaid.ms.gov/wp-content/uploads/2022/07/Healthier-Mississippi-Waiver-Full-Public-Notice-Website.pdf#page=1
   - Relevant pages:
     - #page=1: renewal requested no changes; HMW operated since 2006.
     - #page=2: statewide operation, over 65 or SSI disability, no Medicare, income below 135% FPL, resources under $4,000/$6,000, not otherwise eligible for Medicaid/CHIP/other waiver, MAGI note, and benefit exclusions.
     - #page=3: enrollment cap and waiting list process.

## Requirement Notes

- Eligibility group: aged, blind, or disabled individuals. The CMS STCs use "aged, blind, or disabled"; the state page/fact sheet emphasizes age 65+ or disability. Reuse `is_ssi_aged_blind_disabled`.
- Medicare exclusion: sources use no Medicare / not Medicare eligible / not covered by or entitled to Medicare. Use `is_medicare_eligible` rather than Medicare take-up so HMW eligibility does not change when modeled Medicare enrollment changes. This may understate eligibility for rare age-65+ people who are not actually entitled to Medicare until PolicyEngine has a narrower Medicare entitlement input.
- Pregnancy exclusion: state page and fact sheet say pregnant people cannot qualify. Use `is_pregnant`.
- Long-term care institution exclusion: CMS STCs exclude inpatients in long-term care institutions. Use `is_in_medicaid_facility` as available proxy.
- Income: at or below 135% FPL for the individual/couple, using SSI-based methodology and state-plan exclusions. Reuse `medicaid_optional_senior_or_disabled_countable_income` and the applicant's `marital_unit` so spouses in separate tax units are still counted and dependents do not expand the limit.
- Resources: below $4,000 individual / $6,000 couple. Reuse `ssi_countable_resources` and the applicant's `marital_unit` to match the individual/couple HMW standard.
- Not otherwise eligible: HMW is for people not otherwise eligible for Medicaid state plan, CHIP, or other waiver. Explicitly check existing Medicaid category variables; use a non-circular CHIP child proxy because PolicyEngine's `is_chip_eligible` depends on `is_medicaid_eligible`.
- Enrollment cap: cap is 6,000; allocation/waiting list is not mechanically simulated because PolicyEngine does not have a deterministic slot assignment or current HMW enrollment variable.
