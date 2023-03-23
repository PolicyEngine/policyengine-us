from policyengine_us.model_api import *


class co_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Colorado EITC eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.colorado.gov/sites/default/files/te19_colorado_earned_income_tax_credit.pdf"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        federal_eitc_eligible = tax_unit("eitc_eligible", period)
        return federal_eitc_eligible
