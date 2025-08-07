from policyengine_us.model_api import *


class dividend_income_reduced_by_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Dividend income reduced by investment income"
    documentation = "IRS Form 1040 Schedule D worksheet (part 1 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        qualified_dividend_income = add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        investment_income = tax_unit("investment_income_form_4952", period)
        # dwks04 always assumed to be zero
        floored_investment_income = max_(0, investment_income)
        return max_(0, qualified_dividend_income - floored_investment_income)
