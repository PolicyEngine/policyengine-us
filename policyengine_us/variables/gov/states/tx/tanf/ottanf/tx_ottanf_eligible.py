from policyengine_us.model_api import *


class tx_ottanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas One-Time TANF (OTTANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-802",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # OTTANF eligibility per § 372.802:
        # 1. Must have at least one eligible child
        # 2. Crisis criteria (user input)
        # 3. Income ≤ 200% FPL
        # 4. Resources ≤ $1,000
        # 5. All adults + at least one child meet citizenship
        # 6. Not currently receiving TANF
        # 7. Must be eligible for TANF grant of $10+

        # Must have eligible child (same as regular TANF)
        person = spm_unit.members
        has_eligible_child = spm_unit.any(
            person("tx_tanf_eligible_child", period)
        )

        # Crisis criteria (user input - no formula)
        crisis = spm_unit("tx_ottanf_crisis_criteria", period)

        # Financial eligibility
        income_eligible = spm_unit("tx_ottanf_income_eligible", period)
        resources_eligible = spm_unit("tx_ottanf_resources_eligible", period)

        # Citizenship requirements: all members must be immigration eligible
        immigration_eligible = spm_unit.all(
            person("tx_tanf_immigration_status_eligible_person", period)
        )

        return (
            has_eligible_child
            & crisis
            & income_eligible
            & resources_eligible
            & immigration_eligible
        )
