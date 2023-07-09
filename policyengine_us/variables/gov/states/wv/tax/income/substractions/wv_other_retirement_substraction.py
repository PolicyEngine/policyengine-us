from policyengine_us.model_api import *


class va_other_retirement_subtraction(Variable):
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
        subtractable_other_retirement = min(retirement_income, p.amount)

        return subtractable_other_retirement
