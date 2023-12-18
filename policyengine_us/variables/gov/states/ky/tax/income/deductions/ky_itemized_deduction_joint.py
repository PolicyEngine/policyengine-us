from policyengine_us.model_api import *


class ky_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
