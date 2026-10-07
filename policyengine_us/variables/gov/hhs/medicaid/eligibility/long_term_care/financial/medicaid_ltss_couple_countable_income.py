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
        "and the spouses' qualifying impairment-related work expenses, "
        "then counting half the earnings remainder (DSSM 20200.2(f), "
        "20240.1 and 20240.3; 20 CFR 416.1112(c)(4)-(7)). Each person's "
        "expenses are limited to their own earnings before aggregation. "
        "Other modeled states use the combined income remaining "
        "outside qualified income trusts without exclusions."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78#page=6",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
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
        impairment_expenses = person.marital_unit.sum(
            person("medicaid_ltss_excluded_impairment_related_work_expenses", period)
        )
        countable_earned = (
            max_(
                earned
                - unused_general_disregard
                - p.de.income.earned_disregard
                - impairment_expenses,
                0,
            )
            * p.de.income.earned_income_countable_rate
        )
        delaware_budget = unearned - unearned_disregard + countable_earned
        return where(
            state == state.possible_values.DE, delaware_budget, earned + unearned
        )
