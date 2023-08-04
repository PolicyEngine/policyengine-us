from policyengine_us.model_api import *


class mt_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mt.tax.income.deductions.standard
        agi = tax_unit("mt_agi", period)
        # standard deduction is a percentage of AGI that
        # is bounded by a min/max by filing status.
        min_amount = p.min[filing_status]
        max_amount = p.max[filing_status]
        uncapped_amount = p.rate * agi
        deduction_amount = min_(uncapped_amount, max_amount)

        return max_(deduction_amount, min_amount)
