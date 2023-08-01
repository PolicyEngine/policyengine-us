from policyengine_us.model_api import *


class vt_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        return parameters(period).gov.states.vt.tax.income.deductions.standard
