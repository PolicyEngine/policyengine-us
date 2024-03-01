from policyengine_us.model_api import *


class ut_at_home_parent_credit_one_parent_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Utah at-home parent credit income"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html",
        "https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent

        head_or_spouse_eligible = person("is_tax_unit_head_or_spouse", period)
        one_parent_income_eligible = (
            person("earned_income", period) <= p.parent_max_earnings
        )

        return (head_or_spouse_eligible * one_parent_income_eligible) > 0
