from policyengine_us.model_api import *


class ar_income_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas inflation relief income-tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.cr.tax.income.credits.inflationary_relief
        filing_status = tax_unit("filing_status", period)
        reduction_start = p.start[filing_status]
        increment = p.increment[filing_status]
        reduction_per_increment = p.amount[filing_status]
        excess = max_(reduction_start - agi, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment
        return max_(total_reduction_amount, 0)
