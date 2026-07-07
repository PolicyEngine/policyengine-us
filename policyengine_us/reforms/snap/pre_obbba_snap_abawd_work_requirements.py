"""Pre-OBBBA SNAP ABAWD work requirements counterfactual.

When gov.contrib.snap.pre_obbba_abawd_work_requirements.in_effect is true
for a period, the ABAWD work requirement reverts to pre-OBBBA
(P.L. 119-21, Section 10102) rules for that period in every state:
exempt ages (55+ instead of 65+), the household-child age threshold
(18 instead of 14), and the homeless, veteran, and former foster youth
exemptions.

Scope and limitations:
- Covers the Section 10102 ABAWD exemption and age provisions only.
  Post-OBBBA area waiver geography
  (gov.usda.snap.work_requirements.abawd.waived_county_fips) is not
  reverted, so counterfactual waiver coverage after 2026-10 reflects
  OBBBA-era waiver rules.
- State discretionary exemption flags
  (is_snap_abawd_discretionary_exempt) are assigned at microdata
  construction among the post-OBBBA covered population and are not
  re-drawn under the counterfactual.
- The pre-OBBBA path reads the frozen 2025-06-01 parameter snapshot in
  the baseline formulas, so scheduled pre-OBBBA law changes (the Fiscal
  Responsibility Act sunset on 2030-10-01) are not modeled; the reform
  is intended for analysis windows before then (e.g., 2026/2027).
- The OBBBA-created Indian, Urban Indian, and California Indian
  exemption (7 U.S.C. 2015(o)(3)(F)-(G)) does not exist under the
  counterfactual, so individuals exempt only through it become subject
  to the pre-OBBBA rules. This is the sole case where the reform
  tightens rather than loosens the requirement.
- Medicaid community engagement pass-through eligibility
  (medicaid_community_engagement_pass_through_eligible) evaluates SNAP
  work compliance under whichever SNAP rules are in force, so it also
  reverts under this reform. This is the intended counterfactual: in a
  world without the OBBBA SNAP work requirement, the Medicaid pass-through
  would reference actual (pre-OBBBA) SNAP rules.
"""

from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_pre_obbba_snap_abawd_work_requirements() -> Reform:
    class is_snap_abawd_hr1_in_effect(Variable):
        value_type = bool
        entity = Person
        label = "HR1 ABAWD work requirement changes are in effect for this person"
        definition_period = MONTH
        reference = (
            "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81",
            "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-93.pdf",
        )

        def formula(person, period, parameters):
            p_contrib = parameters(
                period
            ).gov.contrib.snap.pre_obbba_abawd_work_requirements
            # Baseline logic, mirrored from
            # variables/gov/usda/snap/eligibility/work_requirements/
            # is_snap_abawd_hr1_in_effect.py — keep in sync.
            federal = parameters(period).gov.usda.snap.work_requirements.abawd.in_effect
            state_code = person.household("state_code", period.this_year)
            ca = parameters(
                period
            ).gov.states.ca.cdss.snap.work_requirements.abawd.hr1_in_effect
            hi = parameters(
                period
            ).gov.states.hi.dhs.snap.work_requirements.abawd.hr1_in_effect
            ak = parameters(
                period
            ).gov.states.ak.dpa.snap.work_requirements.abawd.hr1_in_effect
            baseline = select(
                [
                    state_code == StateCode.CA,
                    state_code == StateCode.HI,
                    state_code == StateCode.AK,
                ],
                [ca, hi, ak],
                default=federal,
            )
            # Period-gated: only months where the contrib toggle is true
            # revert to pre-OBBBA rules; other months keep baseline
            # behavior, so a future-dated toggle does not apply
            # retroactively.
            return where(p_contrib.in_effect, False, baseline)

    class reform(Reform):
        def apply(self):
            self.update_variable(is_snap_abawd_hr1_in_effect)

    return reform


def create_pre_obbba_snap_abawd_work_requirements_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_pre_obbba_snap_abawd_work_requirements()

    p = parameters.gov.contrib.snap.pre_obbba_abawd_work_requirements
    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_pre_obbba_snap_abawd_work_requirements()
    return None


pre_obbba_snap_abawd_work_requirements = (
    create_pre_obbba_snap_abawd_work_requirements_reform(None, None, bypass=True)
)
