# Idaho regular heating components

The FY2026 components calculate qualified household size, countable income,
income limits, modeled financial eligibility and the heating area. The ordinary
income test is inclusive. A household with a SNAP recipient during the October-September
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
It is not yet connected to a household award because current estimated heating
costs are missing and existing inputs do not identify every heating-cost obligation. Provider/company and
administering-agency distinctions are outside this implementation scope.

The user approved continuing the recovered 44-county heating-area map on
October 20, 2026. `id_liheap_heating_area` derives Areas I-III from the existing
county input using the complete left-hand county table in historical Appendix A.
The right-hand table duplicates Power County and omits Elmore County. The PDF
has no printed effective year; its metadata says last modified October 18, 2006,
and the archived copy was captured January 24, 2017. These dates do not establish
FY2026 applicability. The FY2026 parameter anchor records the approved modeling
continuation. Explicit unknown or unmatched counties return area zero; an omitted
county retains the shared geography fallback to Ada County, Area I.

The FY2025 rent column pays a $75 base amount in every area and burden band,
before the separately determined target supplement. The accepted FY2025 plan
assigns that minimum to households with no specific heat-cost obligation. The
accepted FY2026 plan explicitly makes that category ineligible and the FY2026
matrix drops its rent column. The user initially approved reusing the FY2025
amount, then chose to follow the confirmed FY2026 rule on October 20, 2026.
The conditional rent parameter is therefore $75 for FY2025 and zero from
FY2026 for households without a specific heating-cost obligation. No rent
amount is connected to household awards.
The PY2008 subsidized-housing low-burden rule is excluded. Current housing
responsibility rules are described below.

The approved energy-burden convention is low below 6%, medium from 6% up to
but excluding 11%, and high at 11% or greater (`burden >= 0.11`). This includes
exactly 11% in the high group. The user approved this interpretation on
October 20, 2026: the [FY2026 matrix methodology](https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=2)
prints medium below 11% and high above 11%, leaving exactly 11% unassigned.
The [historical 2011 rule, section 204.03](https://adminrules.idaho.gov/rules/2011/16/0414.pdf#page=8)
explicitly included 11% in high. This is an approved modeling convention;
the current source omission remains documented.

Final eligibility and awards remain incomplete. The current estimated annual
heating-cost chart has not been established, and the PY2007 costs are excluded.
Actual household bills do not replace the state's estimated costs. The
exactly-11-percent boundary is resolved by the approved convention above.

The accepted [FY2025 plan](https://liheapch.acf.gov/docs/2025/state-plans/ID_Plan_2025.pdf#page=9)
establishes the earlier $75 minimum for households without a specific heating
obligation. The accepted [FY2026 plan #page 8-9](https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=8)
requires renters, including subsidized renters, to establish financial heating
responsibility and excludes households with no specific heating-cost obligation.
[IDAPA 16.03.08, sections 200.07 and 201](https://adminrules.idaho.gov/rules/current/16/160308.pdf#page=5),
effective July 1, 2026, likewise requires direct costs or a designated rent
portion. Applying the general fuel/area/burden matrix to otherwise eligible
subsidized households with a heating obligation is an interpretation supported
by these current rules. No current source specifies the old automatic low band.
The existing heat-in-rent flag does not distinguish free bundled heat from a
designated tenant heating charge, so it cannot determine every responsibility
case. No new responsibility input or blanket subsidy exclusion is added.

FY2026 components and the selected electric table are researched and tested; the
incomplete state has no fully verified policy year. Earlier parameter
backfills are unverified historical estimates. Crisis, cooling, weatherization
and equipment are outside scope.
