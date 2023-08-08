from policyengine_us.model_api import *


class mi_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.mi.tax.income.credits.eitc
        return eitc * p.match
