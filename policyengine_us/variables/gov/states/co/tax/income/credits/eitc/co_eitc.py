from policyengine_us.model_api import *


class co_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.colorado.gov/sites/default/files/te19_colorado_earned_income_tax_credit.pdf"
    defined_for = "co_eitc_eligible"

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        match_percent = parameters(
            period
        ).gov.states.co.tax.income.credits.eitc.match
        return federal_eitc * match_percent
