from policyengine_us.model_api import *

class pr_earned_income_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = ""
    definition_period = YEAR
    reference = ""

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        adds = "gov.territories.pr.tax.income.credits.earned_income.ineligible_income_categories"
        investment_income_amount_allowed = adds < p.max_investment_income 
        # check that earned income is above 0?
        return head_or_spouse & investment_income_amount_allowed