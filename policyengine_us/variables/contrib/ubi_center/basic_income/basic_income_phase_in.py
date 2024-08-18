from policyengine_us.model_api import *


class basic_income_phase_in(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic income phase-in"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.basic_income.phase_in
        if p.with_earnings:
            income = tax_unit("tax_unit_earned_income", period)
        else:
            income = add(tax_unit, period, ["irs_gross_income"])
        if p.per_person:
            tax_unit_size = tax_unit("tax_unit_size", period)
            rate = p.rate * tax_unit_size
        else:
            rate = p.rate
        return rate * income
