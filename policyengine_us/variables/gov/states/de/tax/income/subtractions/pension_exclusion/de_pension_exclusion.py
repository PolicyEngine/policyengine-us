from policyengine_us.model_api import *


class de_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6",
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.pension

        # determine age eligibility
        age = person("age", period)

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        cap = p.cap.amount.calc(age)

        eligible_for_pension_exclusion_income = p.age_threshold.calc(age)

        eligible_pension_income = (
            person("taxable_pension_income", period) * head_or_spouse
        )

        eligible_retirement_income = (
            person("de_pension_exclusion_income", period) * head_or_spouse
        )
        # Filers can subtarct only the taxable pension if they are below the age threshold
        # and a larger basket of income of they are abvoe
        eligible_income = where(
            eligible_for_pension_exclusion_income,
            eligible_retirement_income,
            eligible_pension_income,
        )

        # Filers under a certain age, are only eligible to receive
        # a pension exclusion of a max amount pre 2022
        capped_eligible_pension_income = min_(cap, eligible_income)

        # Filer over a certain age are eligible to receive an exclsuion
        # for the total of pension income and eligible retirement income pre and after 2022

        # Filers under a certain age and retired from military,
        # are eligible to receive a pension exclusion of a max amount after 2022
        if p.military_retirement_exclusion_available:
            military_retirement_pay = (
                person("military_retirement_pay", period) * head_or_spouse
            )
            capped_military_retirement_pay = min_(
                p.cap.military, military_retirement_pay
            )
            younger_amount = max_(
                capped_military_retirement_pay, capped_eligible_pension_income
            )
            # Filers under the age threshold, post 2022, can subtract their military retirement
            # income which is capped at a larger amount
            return where(
                eligible_for_pension_exclusion_income,
                capped_eligible_pension_income,
                younger_amount,
            )
        else:
            return capped_eligible_pension_income
