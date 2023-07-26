from policyengine_us.model_api import *


class wv_public_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia public pension subtraction"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        public_pension_income = person(
            "wv_taxable_public_pension_income", period
        )
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.public_pension
        return min_(public_pension_income, p.max_amount)
