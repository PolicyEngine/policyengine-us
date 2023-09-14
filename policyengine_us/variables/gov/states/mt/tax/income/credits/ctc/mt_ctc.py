from policyengine_us.model_api import *


class mt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Child Tax Credit"
    definition_period = YEAR
    unit = USD
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = "mt_ctc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        child_credit = tax_unit.sum(p.amount.calc(age))
        # Credit gets reduced by 90 for each $1,000 over $50,000 of agi
        agi = tax_unit("adjusted_gross_income", period)
        excess = max_(agi - p.reduction.threshold, 0)
        mask = p.reduction.increment != 0
        increments[mask] = excess[mask] // p.reduction.increment[mask]
        reduction_rate = p.reduction.amount * increments
        return max_(child_credit - reduction_rate, 0)
