from openfisca_us.model_api import *


class ca_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "CalEITC eligible"
    unit = bool
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Phase-in until the phase-in earned income amount.
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income
        earnings = tax_unit("earned_income", period)
        meets_earnings_limit = earnings <= p.max_earnings
        investment_income = tax_unit("investment_income", period)
        meets_investment_income_limit = (
            investment_income <= p.max_investment_income
        )
        return meets_earnings_limit & meets_investment_income_limit
