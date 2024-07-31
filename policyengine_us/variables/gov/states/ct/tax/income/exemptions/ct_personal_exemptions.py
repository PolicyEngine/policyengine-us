from policyengine_us.model_api import *


class ct_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Personal Exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        income = tax_unit("ct_agi", period)
        p = parameters(period).gov.states.ct.tax.income.exemptions.personal
        filing_status = tax_unit("filing_status", period)
        max_amount = p.max_amount[filing_status]
        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment
        reduction_per_increment = p.reduction.amount
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        total_reduction_amount = increments * reduction_per_increment
        return max_(max_amount - total_reduction_amount, 0)
