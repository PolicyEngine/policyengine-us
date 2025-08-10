from policyengine_us.model_api import *


class pr_low_income_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Puerto Rico low income credit"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age"
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age_eligible = age >= p.age_threshold
        # if you claim earned income credit, aren't eligible for low income credit
        eitc_not_claimed = (
            person.tax_unit("pr_earned_income_credit", period) <= 0
        )
        return head_or_spouse & age_eligible & eitc_not_claimed
