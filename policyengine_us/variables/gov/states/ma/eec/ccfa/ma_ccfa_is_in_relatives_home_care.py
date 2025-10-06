from policyengine_us.model_api import *


class ma_ccfa_is_in_relatives_home_care(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person is receiving relative or relative's home care"
    definition_period = MONTH
    defined_for = StateCode.MA
