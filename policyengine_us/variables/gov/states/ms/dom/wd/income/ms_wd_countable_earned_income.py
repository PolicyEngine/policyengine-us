from policyengine_us.model_api import *


class ms_wd_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Working Disabled countable earned income"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Countable earned income for Mississippi's Working Disabled program. "
        "This applies the remaining general income exclusion, the flat earned "
        "income exclusion, and the one-half earned-income remainder exclusion. "
        "Student earned income, impairment-related work expenses, blind work "
        "expenses, and PASS exclusions are not modeled."
    )
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32",
        "https://www.medicaid.ms.gov/wp-content/uploads/2014/01/Admin-Code-Part-104.pdf#page=23",
        "https://www.medicaid.ms.gov/wp-content/uploads/2014/01/Admin-Code-Part-104.pdf#page=24",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.wd.eligibility.income.exclusions
        earned_income = person.marital_unit.sum(
            person("ms_wd_gross_earned_income", period)
        )
        unearned_income = max_(
            person.marital_unit.sum(person("ms_wd_gross_unearned_income", period)),
            0,
        )
        remaining_general_exclusion = max_(p.general - unearned_income, 0)
        earned_after_general = max_(earned_income - remaining_general_exclusion, 0)
        earned_after_flat = max_(earned_after_general - p.earned.amount, 0)
        return earned_after_flat * (1 - p.earned.remainder_disregard)
