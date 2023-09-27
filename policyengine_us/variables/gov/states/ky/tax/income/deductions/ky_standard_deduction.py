from policyengine_us.model_api import *


class ky_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        return parameters(period).gov.states.ky.tax.income.deductions.standard
