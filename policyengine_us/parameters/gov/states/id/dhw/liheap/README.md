# Idaho regular heating components

The FY2026 components calculate qualified household size, countable income,
income limits and modeled financial eligibility. The ordinary income test is
inclusive. A household with a SNAP recipient during the October-September
program year, or a current SSI recipient, is categorically income eligible.
Income still determines the eventual award. Any household member can establish
that categorical route; the model does not require every member to receive aid.
A household with no qualified members cannot qualify.

SNAP uses the actual twelve-month program-year window: FY2026 reads October 2025
through September 2026. SSI uses annual positive benefits as a stable-current-
receipt approximation because application month is not an input. The model's
annual income flows likewise approximate the prior-month assessment. Existing
net business inputs receive no second expense deduction. Received sources are
floored separately per person so losses do not cancel other receipts. Social
Security is counted net of the existing Part B premium, floored at zero for
each person; excess premiums cannot reduce pensions or another member's income.
Military retirement pay is counted separately from pension and retirement-account
aggregates. UI uses reported compensation or the shared modeled-state fallback.
TANF is take-up gated and counted once per household, without adding a TANF
categorical route. SPM membership
approximates the household sharing home heating costs.

Means-tested veterans benefits also establish categorical eligibility, but the
existing aggregate veterans_benefits input does not distinguish them from other
VA benefits. That route remains unobserved; a false modeled financial predicate
is not a definitive legal denial for such a household. No new input or blanket
VA qualification is introduced. Housing, heating-cost responsibility and
administrative requirements are separate from this financial component.
The predecessor rule's discretionary catastrophic-illness exception also needs
an administrative determination that existing inputs cannot establish.

The electric-benefit parameter table uses the Idaho Power & Southern Utilities
column for all three heating areas. Electric utility-provider groups are not
distinguished for now; the Avista & Northern Utilities and Rocky Mountain Power
columns are omitted. This is an explicit modeling simplification, not a claim
that providers pay identical benefits. No utility-provider input is added.
The table contains the base amounts before the vulnerable-household supplement.
It is not yet connected to a household award because the area and burden
calculations remain unresolved. Provider/company and administering-agency distinctions are outside this
implementation scope.

The approved energy-burden convention is low below 6%, medium from 6% up to
but excluding 11%, and high at 11% or greater (`burden >= 0.11`). This includes
exactly 11% in the high group. The user approved this interpretation on
October 20, 2026: the [FY2026 matrix methodology](https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=2)
prints medium below 11% and high above 11%, leaving exactly 11% unassigned.
The [historical 2011 rule, section 204.03](https://adminrules.idaho.gov/rules/2011/16/0414.pdf#page=8)
explicitly included 11% in high. This is an approved modeling convention;
the current source omission remains documented.

Final eligibility and awards remain incomplete. The current estimated annual
heating-cost chart and current heating-area mapping have not been established.
The recovered historical county map and 2007 heating
costs are not promoted to FY2026 policy, and actual household bills do not replace
the state's estimated costs. The exactly-11-percent boundary is resolved by the
approved convention above.

FY2026 components and the selected electric table are researched and tested; the
incomplete state has no fully verified policy year. Earlier parameter
backfills are unverified historical estimates. Crisis, cooling, weatherization
and equipment are outside scope.
