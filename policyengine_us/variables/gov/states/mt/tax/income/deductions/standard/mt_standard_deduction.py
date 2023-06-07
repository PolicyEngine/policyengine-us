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
        agi = tax_unit("adjusted_gross_income", period)
        # standard deduction is a percentage of AGI that
        # is bounded by a min/max by filing status.
        min_amount = max_((p.rate * agi), p.min[filing_status])
        return min_(min_amount, p.max[filing_status])