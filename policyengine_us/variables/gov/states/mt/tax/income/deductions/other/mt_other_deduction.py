from policyengine_us.model_api import *


class mt_other_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MT standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        max_amount = p.max[filing_status]

        income = tax_unit("tax_unit_earned_income", period)
        return min_(max_amount, income)
