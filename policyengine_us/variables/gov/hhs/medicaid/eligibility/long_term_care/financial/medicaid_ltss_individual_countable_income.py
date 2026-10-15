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
        "qualified income trust, excluding qualifying interest and dividends "
        "under MEPD E-3331.1 and E-3331.2."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/e-3300-sources-unearned-income",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=10",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=5",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340",
    )

    def formula_2026_01_01(person, period, parameters):
        ssi_exclusions = parameters(period).gov.ssa.ssi.income.exclusions
        state = person.household("state_code", period)
        earned = person("medicaid_ltss_qit_adjusted_earned_income", period)
        unearned = person("medicaid_ltss_qit_adjusted_unearned_income", period)
        needs_based = person("medicaid_ltss_qit_adjusted_needs_based_income", period)
        unearned_disregard = min_(
            max_(unearned - needs_based, 0), ssi_exclusions.general
        )
        unused_general_disregard = max_(ssi_exclusions.general - unearned_disregard, 0)
        impairment_expenses = person(
            "medicaid_ltss_excluded_impairment_related_work_expenses", period
        )
        countable_earned = max_(
            earned
            - unused_general_disregard
            - ssi_exclusions.earned
            - impairment_expenses,
            0,
        ) * (1 - ssi_exclusions.earned_share)
        ordinary_budget = unearned - unearned_disregard + countable_earned
        gross = earned + unearned
        community_spouse_budget = gross - min_(
            max_(gross - needs_based, 0), ssi_exclusions.general
        )
        delaware_budget = where(
            person("medicaid_ltss_has_community_spouse", period),
            community_spouse_budget,
            ordinary_budget,
        )
        washington_excluded = person("wa_medicaid_ltss_excluded_income", period)
        texas_excluded = person(
            "tx_medicaid_ltss_excluded_interest_and_dividends", period
        )
        return where(
            state == state.possible_values.DE,
            delaware_budget,
            max_(gross - washington_excluded - texas_excluded, 0),
        )
