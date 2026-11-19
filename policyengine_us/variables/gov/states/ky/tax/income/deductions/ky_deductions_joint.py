from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class ky_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        itemized = person("ky_itemized_deductions_joint", period)
        standard = person("ky_standard_deduction_joint", period)
        method = person.tax_unit("state_deduction_method", period)
        itemizes = state_itemization_uses_itemized(method, itemized > standard)
        return where(itemizes, itemized, standard)
