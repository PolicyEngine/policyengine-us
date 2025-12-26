from policyengine_us.model_api import *


class ms_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Mississippi TANF eligibility"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-1/",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
    )

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility baseline
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Use federal immigration eligibility baseline
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        income_eligible = spm_unit("ms_tanf_income_eligible", period)
        resources_eligible = spm_unit("ms_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
