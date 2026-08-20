from policyengine_us.model_api import *


class medicaid_ltss_home_equity_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid LTSS home-equity threshold"
    definition_period = MONTH
    documentation = (
        "Applies the 42 USC 1396p(f) substantial home equity payment bar "
        "from explicit home value, encumbrance, fractional-ownership, "
        "resident-exception, and hardship inputs. Washington elects the "
        "federal maximum limit (WAC 182-513-1350(8)(c)); Texas and Delaware "
        "apply the CPI-indexed federal minimum (TX Appendix XXXI; DSSM "
        "20320.7.B and 20320.7.E). Elections in other states are unmodeled: "
        "equity at or below the federal minimum passes, because no state "
        "may bar payment below that amount, and higher equity fails closed. "
        "A person with no equity interest always passes. The agricultural-"
        "land limit in the separate annual "
        "is_medicaid_long_term_care_home_equity_eligible chassis is not "
        "modeled here."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#f",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf#page=3",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care
        state = person.household("state_code", period)
        states = state.possible_values
        home_equity_limit = where(
            state == states.WA,
            p.home_equity.limit,
            p.home_equity.minimum_limit,
        )
        home_value = person("medicaid_ltss_home_market_value", period)
        encumbrances = person("medicaid_ltss_home_encumbrances", period)
        ownership_share = person("medicaid_ltss_home_ownership_share", period)
        valid_ownership_share = (ownership_share >= 0) & (ownership_share <= 1)
        applicant_home_equity = max_(home_value - encumbrances, 0) * ownership_share
        exception = (
            person("medicaid_ltss_home_occupied_by_spouse", period)
            | person(
                "medicaid_ltss_home_occupied_by_child_under_21",
                period,
            )
            | person(
                "medicaid_ltss_home_occupied_by_blind_or_disabled_child",
                period,
            )
            | person(
                "medicaid_ltss_home_equity_hardship_waiver",
                period,
            )
        )

        return valid_ownership_share & (
            exception | (applicant_home_equity <= home_equity_limit)
        )
