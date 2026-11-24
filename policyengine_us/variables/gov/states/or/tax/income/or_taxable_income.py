from policyengine_us.model_api import *


class or_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        or_agi = tax_unit("or_agi", period)
        deductions = tax_unit("or_deductions", period)
        p = parameters(period).gov.states["or"].tax.income.subtractions
        schedule_1a = p.schedule_1a
        if schedule_1a:
            # The Oregon Kids Credit adds these subtractions back to its income base.
            or_agi = or_agi - add(tax_unit, period, schedule_1a)
        return max_(or_agi - deductions, 0)
