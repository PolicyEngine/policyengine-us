from policyengine_us.model_api import *


class mi_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.mi.tax.income.credits.eitc
        return federal_eitc * p.match
