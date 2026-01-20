from policyengine_us.model_api import *


class ia_fip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP eligible"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        # Must have at least one eligible child (uses federal demographic rules)
        has_children = spm_unit("is_demographic_tanf_eligible", period)
        # Must meet immigration status eligibility (citizen or qualified alien)
        # Per Iowa legal code 441—41.23(239B), 41.23(5)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        # Resource eligibility assumed for this simple implementation
        # Actual resource checking would compare spm_unit resources against
        # p.resource_limit_applicant ($2,000) or p.resource_limit_recipient ($5,000)
        income_eligible = spm_unit("ia_fip_income_eligible", period)

        return has_children & immigration_eligible & income_eligible
