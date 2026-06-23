from policyengine_us.model_api import *


class de_non_refundable_credits_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware non-allocable non-refundable credits for each spouse on a separate/combined return"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # On a separate/combined return (Filing Status 4) each spouse's
        # non-refundable credits are limited to that spouse's own tax before
        # credits (Form PIT-RES, Line 32 cannot exceed Line 26 per column).
        # This variable holds the credits that are tied to a specific spouse's
        # column and cannot be moved: each filer's own personal credit and, if
        # age 60 or over, their own aged personal credit. Credits that the
        # filers may allocate between columns (dependents' personal credits,
        # the child/dependent care credit, the non-refundable EITC) are handled
        # in de_non_refundable_credits.
        p = parameters(period).gov.states.de.tax.income.credits.personal_credits
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        personal_credit = is_head_or_spouse * p.personal
        age = person("age", period)
        aged_credit = is_head_or_spouse * p.aged.calc(age)
        return personal_credit + aged_credit
