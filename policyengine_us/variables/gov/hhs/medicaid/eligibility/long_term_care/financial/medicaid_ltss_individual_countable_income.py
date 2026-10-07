from policyengine_us.model_api import *


class medicaid_ltss_individual_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS countable income under an individual budget"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Computes each person's individual income budget independently of "
        "the assistance-unit election. Delaware applies the $20 general "
        "exclusion to non-needs-based unearned income first, then carries "
        "the unused exclusion to earnings before deducting $65 and "
        "counting half the earnings remainder (DSSM 20240.1 and 20240.3). "
        "Applicants with a community spouse receive only the eligible "
        "$20 exclusion (DSSM 20990). Other modeled states use income "
        "remaining outside the qualified income trust without exclusions."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        earned = person("medicaid_ltss_qit_adjusted_earned_income", period)
        unearned = person("medicaid_ltss_qit_adjusted_unearned_income", period)
        needs_based = person("medicaid_ltss_qit_adjusted_needs_based_income", period)
        unearned_disregard = min_(
            max_(unearned - needs_based, 0), p.de.income.general_disregard
        )
        unused_general_disregard = max_(
            p.de.income.general_disregard - unearned_disregard, 0
        )
        countable_earned = (
            max_(earned - unused_general_disregard - p.de.income.earned_disregard, 0)
            * p.de.income.earned_income_countable_rate
        )
        ordinary_budget = unearned - unearned_disregard + countable_earned
        gross = earned + unearned
        community_spouse_budget = gross - min_(
            max_(gross - needs_based, 0), p.de.income.general_disregard
        )
        delaware_budget = where(
            person("medicaid_ltss_has_community_spouse", period),
            community_spouse_budget,
            ordinary_budget,
        )
        return where(state == state.possible_values.DE, delaware_budget, gross)
