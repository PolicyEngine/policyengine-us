from policyengine_us.model_api import *


class ct_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut child tax rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment
        reduction_per_increment = p.reduction.rate * increment

        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment

        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        eligible_child = (age <= p.age_limit) & dependent
        count_children = tax_unit.sum(eligible_child)
        capped_children = min_(count_children, p.child_cap)
        total_rebate = capped_children * p.amount

        return max_(total_rebate - total_reduction_amount, 0)
