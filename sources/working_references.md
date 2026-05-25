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
