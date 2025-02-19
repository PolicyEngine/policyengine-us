from policyengine_us.model_api import *


class pr_earned_income_credit_investment_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Puerto Rico earned income credit investment income"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30211-earned-income-credit"

    adds = "gov.territories.pr.tax.income.credits.earned_income.investment_income.sources"
