from policyengine_us.model_api import *


class medicaid_ltss_couple_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS countable income under a couple budget"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Computes the spouses' combined income budget independently of "
        "the assistance-unit election, returning the same combined amount "
        "for each spouse. Delaware applies one $20 general exclusion to "
        "the couple's non-needs-based unearned income first, then carries "
        "the unused exclusion to combined earnings before deducting $65 "
        "and counting half the earnings remainder (DSSM 20240.1 and "
        "20240.3). Other modeled states use the combined income remaining "
        "outside qualified income trusts without exclusions."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        earned = person.marital_unit.sum(
            person("medicaid_ltss_qit_adjusted_earned_income", period)
        )
        own_unearned = person("medicaid_ltss_qit_adjusted_unearned_income", period)
        unearned = person.marital_unit.sum(own_unearned)
        needs_based = person.marital_unit.sum(
            person("medicaid_ltss_qit_adjusted_needs_based_income", period)
        )
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
        delaware_budget = unearned - unearned_disregard + countable_earned
        return where(
            state == state.possible_values.DE, delaware_budget, earned + unearned
        )
