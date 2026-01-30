from policyengine_us.model_api import *


class il_ihwap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois IHWAP eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/6862#7",
        "https://dceo.illinois.gov/communityservices/homeweatherization.html",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("il_ihwap_income_eligible", period)
        categorically_eligible = spm_unit(
            "il_ihwap_categorically_eligible", period
        )
        return income_eligible | categorically_eligible
