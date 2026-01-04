from policyengine_us.model_api import *


class tn_ff_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee Families First eligible"
    definition_period = MONTH
    reference = "https://www.tn.gov/humanservices/for-families/families-first-tanf/families-first-eligibility-information.html"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Must meet demographic requirements (minor child with parent/relative)
        # Use federal demographic eligibility directly
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one citizen or legal immigrant
        # Use federal immigration eligibility directly
        has_citizen = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Must meet income eligibility
        income_eligible = spm_unit("tn_ff_income_eligible", period)

        # Must meet resource eligibility
        resources_eligible = spm_unit("tn_ff_resources_eligible", period)

        # All requirements must be met
        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resources_eligible
        )
