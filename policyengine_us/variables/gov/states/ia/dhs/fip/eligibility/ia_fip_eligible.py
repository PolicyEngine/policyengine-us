from policyengine_us.model_api import *


class ia_fip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf"
    )

    def formula(spm_unit, period, parameters):
        # Must have at least one eligible child (uses federal demographic rules)
        has_children = spm_unit("is_demographic_tanf_eligible", period)
        # Must meet immigration status eligibility (citizen or qualified alien)
        # Per Iowa legal code 441—41.23(239B), 41.23(5)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        resources_eligible = spm_unit("ia_fip_resources_eligible", period)
        income_eligible = spm_unit("ia_fip_income_eligible", period)

        return (
            has_children
            & immigration_eligible
            & resources_eligible
            & income_eligible
        )
