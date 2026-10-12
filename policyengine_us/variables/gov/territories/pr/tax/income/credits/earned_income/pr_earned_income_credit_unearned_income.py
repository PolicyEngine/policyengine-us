from policyengine_us.model_api import *


class pr_earned_income_credit_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Puerto Rico earned income credit unearned income"
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1007/subchapter-b/30211/"

    adds = "gov.territories.pr.tax.income.credits.earned_income.unearned_income.sources"
