from policyengine_us.model_api import *


class ky_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky standard deduction when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return (is_head | is_spouse) * parameters(
            period
        ).gov.states.ky.tax.income.deductions.standard
