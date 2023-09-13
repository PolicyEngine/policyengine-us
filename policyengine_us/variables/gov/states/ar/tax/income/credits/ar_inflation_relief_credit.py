from policyengine_us.model_api import *


class ar_inflation_relief_credit(Variable):
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
        ).gov.states.ar.tax.income.credits.inflationary_relief
        filing_status = tax_unit("filing_status", period)
        max_amount = p.max_amount[filing_status]
        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment[filing_status]
        reduction_per_increment = p.reduction.amount[filing_status]
        excess = max_(agi - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment
        return max_(max_amount - total_reduction_amount, 0)
