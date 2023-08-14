from policyengine_us.model_api import *


class ky_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "KY aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        aged = tax_unit("aged", period)
        p = parameters(period).gov.states.ky.tax.income.exemptions.aged
        return aged * p.amount
