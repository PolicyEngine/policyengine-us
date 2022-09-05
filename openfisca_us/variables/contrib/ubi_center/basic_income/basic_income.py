from openfisca_us.model_api import *


class basic_income(Variable):
    value_type = float
    entity = Person
    label = "Basic income"
    unit = USD
    documentation = "Total basic income payments for this person. Phase-outs as an equal percentage to all tax unit members."
    definition_period = YEAR

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
