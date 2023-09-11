from policyengine_us.model_api import *


class la_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana military pay exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.military_pay_exclusion
        compensation = add(tax_unit, period, ["military_retirement_pay"])
        return min_(max_amount, compensation)
