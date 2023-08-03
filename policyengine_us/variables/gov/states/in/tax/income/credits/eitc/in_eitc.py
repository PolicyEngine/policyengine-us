from policyengine_us.model_api import *


class in_eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Indiana Earned Income Tax Credit"
    unit = USD
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.credits.eitc
        eitc = tax_unit("earned_income_tax_credit", period)  # needs to be > 0
        return eitc * p.match
