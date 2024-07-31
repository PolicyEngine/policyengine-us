from policyengine_us.model_api import *


class al_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama casualty loss deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        loss = add(tax_unit, period, ["casualty_loss"])
        deduction = parameters(period).gov.irs.deductions.itemized.casualty
        al_agi = tax_unit("al_agi", period)
        return max_(0, loss - al_agi * deduction.floor)
