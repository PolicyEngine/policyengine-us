from policyengine_us.model_api import *


class wv_other_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia other retirement subtraction"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(tax_unit, period, parameters):
        retirement_income = tax_unit("wv_retirement_income", period)
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.other_retirement
        return min(retirement_income, p.max_amount)
