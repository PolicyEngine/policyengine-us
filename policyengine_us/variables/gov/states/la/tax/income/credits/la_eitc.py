from policyengine_us.model_api import *


class la_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=453085"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        match_percent = parameters(
            period
        ).gov.states.la.tax.income.credits.eitc.match
        return federal_eitc * match_percent
