from policyengine_us.model_api import *


class la_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=453085"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.la.tax.income.credits
        return federal_eitc * p.eitc.match
