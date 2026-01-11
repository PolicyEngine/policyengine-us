from policyengine_us.model_api import *


class md_tca_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TCA eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://dsd.maryland.gov/regulations/Pages/07.03.03.03.aspx",
        "https://dsd.maryland.gov/regulations/Pages/07.03.03.12.aspx",
    )

    def formula(spm_unit, period, parameters):
        # Must have at least one eligible child (uses federal demographic rules)
        has_children = spm_unit("is_demographic_tanf_eligible", period)

        # Must meet income eligibility
        income_eligible = spm_unit("md_tca_income_eligible", period)

        # Must meet immigration status eligibility (citizen or qualified alien)
        # Per COMAR 07.03.17.09 and 8 USC 1641
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Note: Per COMAR 07.03.03.12, individual assets are EXCLUDED
        # from TCA eligibility, so no resource test is required.

        return has_children & income_eligible & immigration_eligible
