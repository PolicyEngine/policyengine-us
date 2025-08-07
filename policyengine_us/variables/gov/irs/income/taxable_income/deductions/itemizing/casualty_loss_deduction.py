from policyengine_us.model_api import *


class casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Casualty loss deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        loss = add(tax_unit, period, ["casualty_loss"])
        p = parameters(period).gov.irs.deductions.itemized.casualty
        positive_agi = tax_unit("positive_agi", period)
        amount_over_floor = max_(0, loss - positive_agi * p.floor)
        return p.active * amount_over_floor
