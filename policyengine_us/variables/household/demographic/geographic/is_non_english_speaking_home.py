from policyengine_us.model_api import *


class is_non_english_speaking_home(Variable):
    value_type = bool
    entity = Household
    label = "Primary language spoken at home is not English"
    definition_period = YEAR
