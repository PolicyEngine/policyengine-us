from policyengine_us.model_api import *


class hi_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii TANF"
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/",
        "https://humanservices.hawaii.gov/bessd/tanf/",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        # Demographic eligibility (federal baseline)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Gross income eligibility
        gross_income_eligible = spm_unit(
            "hi_tanf_gross_income_eligible", period
        )

        # NOTE: Hawaii disregards assets since April 18, 2013
        # No resource test is applied

        return demographic_eligible & gross_income_eligible
