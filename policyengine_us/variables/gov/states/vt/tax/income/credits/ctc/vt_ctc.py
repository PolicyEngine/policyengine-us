from policyengine_us.model_api import *


class vt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child tax credit"
    definition_period = YEAR
    unit = USD
    reference = "https://legislature.vermont.gov/statutes/section/32/151/05830f"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # Get age status of all people in the tax unit.
        person = tax_unit.members
        age = person("age", period)
        p = parameters(period).gov.states.vt.tax.income.credits.ctc
        eligible = age <= p.age_limit
        count_eligible = tax_unit.sum(eligible)
        # Get adjusted gross income.
        agi = tax_unit("adjusted_gross_income", period)
        # 5830f(b): "the amount of the credit per child" is reduced, but not
        # below zero, by $20 for each $1,000 of AGI over $125,000.
        excess_agi = max_(agi - p.reduction.start, 0)
        increments = np.ceil(excess_agi / p.reduction.increment)
        reduction_per_child = p.reduction.amount * increments
        credit_per_child = max_(p.amount - reduction_per_child, 0)
        return count_eligible * credit_per_child
