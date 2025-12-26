from policyengine_us.model_api import *


class ne_adc_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nebraska ADC eligible"
    definition_period = MONTH
    reference = (
        "https://dhhs.ne.gov/Pages/TANF.aspx",
        "https://dhhs.ne.gov/Pages/Title-468.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility baseline
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Check immigration eligibility (at least one citizen/legal immigrant)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        # Income eligibility
        income_eligible = spm_unit("ne_adc_income_eligible", period)
        # Resource eligibility (YEAR variable)
        resources_eligible = spm_unit(
            "ne_adc_resources_eligible", period.this_year
        )
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
