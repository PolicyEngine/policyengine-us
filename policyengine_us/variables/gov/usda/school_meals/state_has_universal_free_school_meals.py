from policyengine_us.model_api import *


class state_has_universal_free_school_meals(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "State has universal free school meals"
    documentation = (
        "Whether the SPM unit lives in a state that offers free breakfast "
        "and lunch to all students regardless of household income."
    )
    reference = "https://frac.org/hsmfa-report-2024"

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        return parameters(period).gov.usda.school_meals.state_universal_free_meals[
            state
        ]
