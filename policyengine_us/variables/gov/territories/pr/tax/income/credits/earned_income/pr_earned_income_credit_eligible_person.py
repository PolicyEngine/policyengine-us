from policyengine_us.model_api import *


class pr_earned_income_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico earned income credit eligible person"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        unearned_income = person(
            "pr_earned_income_credit_unearned_income", period
        )
        unearned_income_amount_under_limit = (
            unearned_income <= p.unearned_income.limit
        )

        age = person("age", period)
        age_within_range = age >= p.eligibility.min

        filing_status = person.tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE

        eligible = (
            head_or_spouse
            & unearned_income_amount_under_limit
            & age_within_range
        )
        # if separate filers are eligible
        if p.eligibility.separate_filer:
            return eligible
        # else, filing status can't be filing separate
        else:
            return eligible & not_separate
