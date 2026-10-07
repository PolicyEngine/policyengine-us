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
        "qualifying impairment-related work expenses, then counting "
        "half the earnings remainder (DSSM 20200.2(f), 20240.1 and "
        "20240.3; 20 CFR 416.1112(c)(4)-(7)). "
        "Applicants with a community spouse receive only the eligible "
        "$20 exclusion (DSSM 20990). Washington removes representable "
        "WAC 182-513-1340 source exclusions before the SIL comparison "
        "and income budget. Texas uses income remaining outside the "
        "qualified income trust."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78#page=6",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340",
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
        impairment_expenses = person(
            "medicaid_ltss_excluded_impairment_related_work_expenses", period
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
        washington_excluded = person("medicaid_ltss_wa_excluded_income", period)
        return where(
            state == state.possible_values.DE,
            delaware_budget,
            max_(gross - washington_excluded, 0),
        )
