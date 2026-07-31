from policyengine_us.model_api import *


class is_ccdf_continuous_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Whether the SPM unit meets an unmodeled continuous CCDF income test"
    documentation = (
        "Intentional input for state programs whose continuing income rules "
        "are not modeled from household income."
    )
