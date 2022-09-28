from openfisca_us.model_api import *


class basic_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income"
    unit = USD
    documentation = "Total basic income payments for this filer."
    definition_period = YEAR

<<<<<<< HEAD
    def formula(person, period, parameters):
        eligible = person.tax_unit("basic_income_eligible", period)
        basic_income = person("basic_income_before_phase_out", period)
        tax_unit = person.tax_unit
        tax_unit_basic_income = tax_unit.sum(basic_income)
        tax_unit_phase_out = tax_unit("basic_income_phase_out", period)
        percent_reduction = where(
            tax_unit_basic_income > 0,
            tax_unit_phase_out / tax_unit_basic_income,
            0,
        )
        return basic_income * eligible * (1 - percent_reduction)
=======
    def formula(tax_unit, period, parameters):
        eligible = tax_unit("basic_income_eligible", period)
        basic_income = tax_unit("basic_income_before_phase_out", period)
        phase_out = tax_unit("basic_income_phase_out", period)
        return eligible * (basic_income - phase_out)
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
