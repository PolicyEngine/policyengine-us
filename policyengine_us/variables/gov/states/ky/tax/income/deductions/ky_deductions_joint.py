from policyengine_us.model_api import *


class ky_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        return max_(
            person("ky_itemized_deductions_joint", period),
            person("ky_standard_deduction_joint", period),
        )
