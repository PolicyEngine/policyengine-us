from policyengine_us.model_api import *


class ct_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut child tax rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment
        reduction_per_increment = p.reduction.rate * increment

        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment

        count_dependents = tax_unit("tax_unit_count_dependents", period)
        capped_children = min_(count_dependents, p.child_cap)
        total_rebate = capped_children * p.amount

        return max_(total_rebate - total_reduction_amount, 0)
