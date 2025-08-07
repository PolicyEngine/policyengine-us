from policyengine_us.model_api import *


class mt_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "The total amount of Montana deductions and exemptions when married filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        standard_deduction = person("mt_standard_deduction_indiv", period)
        itemized_deductions = person("mt_itemized_deductions_indiv", period)
        itemizes = person.tax_unit("mt_tax_unit_itemizes", period)
        return where(itemizes, itemized_deductions, standard_deduction)
