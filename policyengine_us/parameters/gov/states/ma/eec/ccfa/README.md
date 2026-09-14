# Massachusetts CCFA income rules

This update covers countable income only. Asset tests, service needs, fee rules,
and authorization history are tracked separately in
[issue #9456](https://github.com/PolicyEngine/policyengine-us/issues/9456).

## Effective dates

| Date | Income rule and primary evidence |
| --- | --- |
| February 1, 2022 documented baseline | The [policy guide, pp. 36–40](https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=37) excludes dependent earnings and permits deductions for child support and alimony paid. Dependent unearned income still counts. This is a documented baseline, not a finding of the original enactment date. |
| October 1, 2023 | The [operational advisory, pp. 2–3](https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=3) excludes SSI, SSDI, child support and TAFDC. The [CCDF plan amendment, p. 61](https://www.mass.gov/doc/ma-eec-ccdf-state-plan-fy-2022-2024-amend-4/download#page=61) explicitly dates broader Social Security and dependent-income exclusions to October 1. |
| April 30, 2024 | The [operational advisory, p. 3](https://www.mass.gov/doc/eec-policy-advisory-field-operations-7-child-care-financial-assistance-updated-policy-guidance/download#page=3) implements the veterans disability exclusion; the [May refresher, p. 19](https://www.mass.gov/doc/may-2024-ccfa-policy-refresher-slide-deck-0/download#page=19) labels it new. The parameter preserves April 30; monthly calculations first reflect it in May. |
| April 1, 2025 coverage | [CCFA-25-03, pp. 5–6](https://archives.lib.state.ma.us/server/api/core/bitstreams/5c538ae6-69c2-43df-bf85-10d2f5e5bfc2/content#page=6) discusses PFML payments. This is the earliest explicit evidence located, not proof PFML first became countable then. Earlier coverage needs further research. |
| January 1, 2026 | [December 2025 training, pp. 5–7](https://www.mass.gov/doc/december-2025-ccfa-policy-and-procedure-slides/download#page=5) excludes earned income of any minor, including minor parents. The general 85% SMI entry limit is already encoded. |

The [May 6, 2026 consolidated manual, pp. 21–23](https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=21)
corroborates current rules. Its publication date is not the effective date of all
exclusions: implementation was phased.

## Input contracts

- `ma_pfml_received` records annual Massachusetts PFML cash benefits received.
  `ma_paid_leave_taxable_wages` records contribution wages and is not a substitute.
  PFML receipts feed CCFA only in this update; mappings to other programs and taxes
  require separate policy work. Receipt alone does not establish a service need.
- `veterans_disability_benefits` is an annual subset of `veterans_benefits`.
  Supplying the subtype alone populates the shared total. When supplying both,
  include disability in the total; CCFA subtracts at most that total. The generic
  total alone remains countable because its disability portion is unknown.
  Military retirement remains countable. The shared total retains its existing
  dataset uprating treatment.
- `ma_ccfa_is_parent` identifies a resident parent of an applicant child. Its
  default uses adult tax heads/spouses or known minor parents. Override for complex
  households, including parents who are tax dependents and nonparent relatives.
  `ma_ccfa_is_nonparent_caregiver_family` identifies a family with no resident
  parent and excludes caregiver income by default. It does not change fee rules
  in this income-only update.
- Before October 2023, tax dependency approximates dependent family membership.
  Dependent earnings, including those of dependent college students, are excluded;
  their unearned income counts. Resident-parent support and alimony paid are
  deducted from the household total, without a payer-income cap. Final countable
  income is floored at zero.
- Self-employment includes `farm_operations_income` and
  `partnership_s_corp_income`; other sources include `farm_rent_income` and
  recurring `estate_income`. Passive partnership income is an unearned subset,
  not an additional source. `farm_income` is Schedule J income averaging, not
  ordinary farm income. [EEC procedures, Appendix A](https://www.mass.gov/doc/financial-assistance-procedures-manual-for-subsidy-administrators/download#page=114)
  cover farmers and partnerships. Tax inputs approximate EEC net business income;
  adjustments for disallowed expenses remain outside this update. Avoid reporting
  the same receipts under multiple overlapping income inputs.
- Both manuals explicitly count lottery earnings. They do not establish that all
  `gambling_winnings` count. A lottery input contract remains in issue #9456.

Special historical VA exclusions, earlier PFML coverage, and exact CCFA family
membership also remain follow-up work. The policy audit is recorded in
[issue #9455](https://github.com/PolicyEngine/policyengine-us/issues/9455).
