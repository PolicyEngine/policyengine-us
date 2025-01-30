from policyengine_us.model_api import *


class pr_earned_income_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico earned income credit eligibility"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30211-earned-income-credit"

    def formula(person, period, parameters):
        # workflow: 
        # WRITE ME:
        # taxpayer or spouse must be 19 or older, not a dependent, not filing as married filing separately
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income.investment_income
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        investment_income = person(
            "pr_earned_income_credit_investment_income", period
        )
        investment_income_amount_under_limit = investment_income <= p.limit
        return head_or_spouse & investment_income_amount_under_limit
