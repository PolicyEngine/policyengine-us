from policyengine_us.model_api import *


class takes_up_itemized_medical_deduction(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Takes up the itemized medical deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if not hasattr(tax_unit.simulation, "dataset"):
            return True
        takeup_rate = parameters(
            period
        ).gov.irs.deductions.itemized.medical.takeup
        return random(tax_unit) < takeup_rate
