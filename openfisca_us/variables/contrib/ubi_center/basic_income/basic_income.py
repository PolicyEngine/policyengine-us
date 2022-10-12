from policyengine_us.model_api import *


class basic_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income"
    unit = USD
    documentation = "Total basic income payments for this filer."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("basic_income_eligible", period)
        basic_income = tax_unit("basic_income_before_phase_out", period)
        phase_out = tax_unit("basic_income_phase_out", period)
        return eligible * (basic_income - phase_out)
