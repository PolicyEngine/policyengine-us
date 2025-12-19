from policyengine_us.model_api import *


class is_non_english_speaking_home(Variable):
    value_type = bool
    entity = Household
    label = "Non-English speaking home"
    definition_period = YEAR
    documentation = "Whether the household's primary language is not English"
