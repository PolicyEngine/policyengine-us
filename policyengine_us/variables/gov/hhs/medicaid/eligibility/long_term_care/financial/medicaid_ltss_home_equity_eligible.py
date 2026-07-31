from policyengine_us.model_api import *


class medicaid_ltss_home_equity_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS home-equity threshold"
    definition_period = MONTH
    documentation = (
        "Models the separate LTSS home-equity payment bar from explicit home "
        "value, encumbrance, fractional-ownership, resident-exception, and "
        "hardship inputs. Texas and Washington have sourced 2026 caps. "
        "Delaware remains unmodeled because the cited sources do not establish "
        "a state-issued numeric 2026 cap."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values

        home_equity_limit = select(
            [state == states.TX, state == states.WA],
            [p.tx.home_equity.limit, p.wa.home_equity.limit],
            default=0,
        )
        home_cap_is_modeled = (state == states.TX) | (state == states.WA)
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

        return (
            (pathway != pathways.UNMODELED)
            & valid_ownership_share
            & (
                exception
                | (home_cap_is_modeled & (applicant_home_equity <= home_equity_limit))
            )
        )
