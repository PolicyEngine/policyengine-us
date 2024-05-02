from policyengine_us.model_api import *


class co_pension_subtraction_indv(Variable):
    value_type = float
    entity = Person
    label = "Colorado pension and annuity subtraction for eligible individuals"
    defined_for = "co_pension_subtraction_indv_eligible"
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(4)(g)(III)
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        taxable_pension_income = person(
            "co_pension_subtraction_income", period
        )
        pension_survivors = person("pension_survivors", period)
        co_social_security_subtraction = person(
            "co_social_security_subtraction_indv", period
        )
        age = person("age", period)
        # The maximum subtarction amount is reduced by the social security subtraction amount
        reduced_older_cap = max_(
            p.cap.older - co_social_security_subtraction, 0
        )
        reduced_younger_cap = max_(
            p.cap.younger - co_social_security_subtraction, 0
        )

        capped_older_amount = min_(reduced_older_cap, taxable_pension_income)
        capped_middle_amount = min_(
            reduced_younger_cap, taxable_pension_income
        )
        capped_younger_amount = min_(reduced_younger_cap, pension_survivors)

        return select(
            [
                age >= p.age_threshold.older,
                age >= p.age_threshold.younger,
            ],
            [capped_older_amount, capped_middle_amount],
            default=capped_younger_amount,
        )
