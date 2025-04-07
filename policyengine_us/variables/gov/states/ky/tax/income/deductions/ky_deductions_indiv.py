from policyengine_us.model_api import *


class ky_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky income deductions when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        itemizes = person.tax_unit("ky_tax_unit_itemizes", period)
        itemized = person("ky_itemized_deductions_indiv", period)
        standard = person("ky_standard_deduction_indiv", period)
        return where(itemizes, itemized, standard)
