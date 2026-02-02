from policyengine_us.model_api import *


class ga_retirement_exclusion_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Countable earned income for the Georgia retirement exclusion for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download",  # Page 15
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",  # Page 15
        "https://law.justia.com/codes/georgia/title-48/chapter-7/article-2/section-48-7-27/",  # (a)(5)(E)(i)
    )
    defined_for = StateCode.GA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ga.tax.income.agi.exclusions.retirement.cap
        # Business income is included in the earned income concept for the Georgia retirement income exclusion
        earned_income = add(
            person, period, ["earned_income", "partnership_s_corp_income"]
        )
        return min_(p.earned_income, earned_income)
