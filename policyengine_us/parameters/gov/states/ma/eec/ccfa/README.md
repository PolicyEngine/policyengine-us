# Child Care Financial Assistance

## Policy history

The May 6, 2026 consolidated manual combines changes implemented in stages. Its
publication date is not the effective date of every income exclusion.

| Date | Rule and evidence | Model treatment |
| --- | --- | --- |
| February 1, 2022 baseline | [Policy guide](https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=37), pp. 36–40, 76: dependent earnings excluded; support and alimony paid deductible; assets at or below $1 million; homeless asset exemption; initial 85% SMI exception for a disabled child; caregiver fee exemption and half fees for part-time care. | Correct historical omissions from this documented baseline. This does not establish their original enactment dates. |
| October 1, 2023 | [Operational advisory](https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=3), pp. 2–3, removes SSI, SSDI, child support and TAFDC from countable income; waives income collection and fees for homeless families. [CCDF plan amendment](https://www.mass.gov/doc/ma-eec-ccdf-state-plan-fy-2022-2024-amend-4/download#page=61) explicitly dates the broader Social Security and dependent-income exclusions to October 1. | Exclude Social Security (including retirement and survivors), SSI, child support and nonparent income; apply homeless income and fee exemptions. |
| April 30, 2024 | [Operational advisory](https://www.mass.gov/doc/eec-policy-advisory-field-operations-7-child-care-financial-assistance-updated-policy-guidance/download#page=3), p. 3, implements veterans disability exclusion. [May refresher](https://www.mass.gov/doc/may-2024-ccfa-policy-refresher-slide-deck-0/download#page=19) labels it NEW. | Exclude the disability subset of veterans benefits. Store April 30 exactly; first-of-month monthly calculations first reflect it in May. The 2023 manual adopted this exclusion before operational rollout. |
| April 1, 2025 | [CCFA-25-03](https://archives.lib.state.ma.us/server/api/core/bitstreams/5c538ae6-69c2-43df-bf85-10d2f5e5bfc2/content#page=5), pp. 5–6: Pathway to Full-Time Employment, parental leave, domestic violence, substance use treatment and military deployment service needs. PFML payments are discussed under parental leave. | Accept active, approved service-need statuses. Count actual PFML receipts from this earliest explicit evidence found; this is a coverage date, not a claim PFML first became countable then. |
| January 1, 2026 | [December 2025 training](https://www.mass.gov/doc/december-2025-ccfa-policy-and-procedure-slides/download#page=5), pp. 5–7: initial income limit rises from 50% to 85% SMI; excludes earned income of any minor and income of siblings not receiving CCFA. | The general 85% entry limit was already encoded. Extend the earnings exclusion to minor parents; nonparent income is already excluded. |
| May 6, 2026 | [Consolidated manual](https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=21), pp. 21–23, 28–35, 44–46. | Corroborates current income, asset, service and fee rules. Portal/waitlist procedures do not change the static benefit calculation. |

The 2023 advisory explicitly says implementation is phased. Do not infer operational
dates solely from the October 2023 manual. The May 2026 manual retains homelessness
service and fee exemptions but omits the prior explicit no-income-collection sentence;
the model retains the October 2023 waiver because no repeal was identified.

## Income inputs and household roles

- `ma_pfml_received` is annual Massachusetts PFML **cash benefits actually received**,
  not wages subject to PFML contributions. Do not add `ma_paid_leave_taxable_wages` to
  countable income. These receipts currently feed CCFA only; tax and other benefit
  program mappings require separate policy work.
- `veterans_disability_benefits` is an annual subset of `veterans_benefits`. Supplying
  the subtype alone also populates the shared total. When supplying both, include
  disability in the total; CCFA subtracts at most that total. The generic total alone
  remains countable because it cannot establish which payments are disability.
  Military retirement remains countable. Special VA-related exclusions in the 2022
  guide (e.g. certain payments to children of Vietnam veterans) need more subtypes.
- `ma_ccfa_is_parent` identifies a parent residing with a child applying for CCFA.
  Its default infers adult tax heads/spouses (or known minor parents). Override it
  for complex households, including a parent who is a tax dependent, separate tax
  filers who are nonparent relatives, or nonparent caregivers. Setting
  `ma_ccfa_is_nonparent_caregiver_family` identifies a family with no resident parent,
  excludes caregiver income by default and waives parent fees.
- Before October 2023, tax dependency approximates required dependent membership.
  Dependent earnings are excluded, including those of dependent college students;
  their unearned income counts. The 2022 guide permits support paid to be deducted
  from total household income. No later policy establishes a payer-income cap:
  resident-parent support payments remain deducted from the household total, with
  a zero floor on final countable income.
- Self-employment includes `farm_operations_income` and `partnership_s_corp_income`;
  unearned sources include `farm_rent_income` and recurring `estate_income`. Passive
  partnership income is an unearned subset, not an additional source. Do not use
  `farm_income` (Schedule J income averaging) as ordinary farming receipts.
  [EEC procedures, Appendix A](https://www.mass.gov/doc/financial-assistance-procedures-manual-for-subsidy-administrators/download#page=114)
  cover farmers and partnerships. Tax income inputs remain an approximation of EEC
  net business income: expense adjustments such as disallowed depreciation are not
  separately modeled. Avoid duplicating receipts across overlapping input categories.
- Both older and current manuals explicitly name **lottery** earnings. They do not
  establish that every component of `gambling_winnings` counts. No broad gambling
  mapping or new lottery variable is added pending a precise input contract.

## Service needs and fees

The `ma_ccfa_approved_*` monthly inputs record a valid, active authorization for
parental leave, Pathway, domestic violence, substance use treatment or military
deployment. They do not calculate agency approval or extend an expired authorization.
Pathway approval includes the 15–less-than-25-hour employment/combined-activity rule,
12-month duration and prohibition on consecutive use at reauthorization. Parental
leave is limited to one parent; it does not waive the other parent's service need.
Military deployment does. PFML receipt alone is not proof of qualifying parental leave.
The ordinary part-time work floor remains 20 hours.

`ma_ccfa_has_part_time_authorization` halves the child's fee after applying sibling
discounts in youngest-child order. It must reflect actual authorization, not simply
a before/after-school schedule. The default full-time assumption and counting all
eligible children as subsidized children remain approximations.

## Remaining rule coverage

Tracked in [issue #9456](https://github.com/PolicyEngine/policyengine-us/issues/9456).

The following require additional inputs or administrative history. This update does
not claim complete CCFA eligibility or case-management coverage:

- Full-time service threshold changed from 30 to 25 hours; April 30, 2024 guidance
  also changed college full-time status from 12 to 10 credits and allowed certain
  graduate study at reauthorization. General student status remains a proxy; numeric
  education/training hours, study level and prior service need are not represented.
- April 1, 2025 replaced unlimited 26-week provisional authorizations with limited
  12-week periods and ended their blanket fee waiver. Approval and renewal history
  are required to calculate these rules rather than accept a verified status.
- DTA/DCF referral eligibility, transitional periods (24 months from October 2023),
  actual referral-based asset/fee exemptions, and the first transitional year fee
  waiver need referral/case-closure data. Existing TAFDC-eligibility proxies remain.
- Authorization fee locks, aging-out/school-year continuity, allocation priorities,
  family composition beyond SPM/tax-unit proxies, and additional qualifying immigration
  statuses need further work. Only the child's immigration status is assessed.
- Disability, retirement and full-time-student inputs approximate verified service
  needs. One parent's disability or pregnancy alone does not exempt the whole family.

Annual provider rates and fee-table amounts were outside this rule-history audit.
