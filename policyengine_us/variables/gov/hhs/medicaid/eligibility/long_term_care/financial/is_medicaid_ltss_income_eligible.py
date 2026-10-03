from policyengine_us.model_api import *


class is_medicaid_ltss_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS income threshold"
    definition_period = MONTH
    documentation = (
        "Tests only the income threshold for the selected modeled Medicaid "
        "LTSS financial pathway. QIT-adjusted income and Washington medically "
        "needy expenses and cost of care are trusted inputs; this variable "
        "does not validate a trust, expense, service, or facility rate. The "
        "Washington institutional branch models the WAC 182-513-1395(4) "
        "payment threshold using income only: the excess-resources term in "
        "subsection (4)(a) is unmodeled (slightly lenient; resources are "
        "screened separately), as are the three- or six-month spenddown "
        "process in subsection (5) and the WAC 182-515-1507 categorically "
        "needy route that bypasses the special income limit. The Delaware "
        "special income limit is 250% of the SSI standard (DSSM 20100.2.2), "
        "and its $20 disregard with the needs-based carve-out follows DSSM "
        "20240.1 and 20990."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/2026/06/2026-SSI-Related-Income-Standards-and-Medicare-Premiums.pdf",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-515-1508",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        setting = person("medicaid_ltss_setting", period)
        settings = setting.possible_values
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values
        assistance_unit_size = person("medicaid_ltss_assistance_unit_size", period)
        income = person("medicaid_ltss_qit_adjusted_income", period)

        special_income_limit = select(
            [
                (state == states.TX) & (assistance_unit_size == 1),
                (state == states.TX) & (assistance_unit_size == 2),
                (state == states.DE) & (assistance_unit_size == 1),
                (state == states.DE) & (assistance_unit_size == 2),
                (state == states.WA) & (assistance_unit_size == 1),
            ],
            [
                p.tx.special_income_limit.individual,
                p.tx.special_income_limit.couple,
                p.de.special_income_limit.individual,
                p.de.special_income_limit.couple,
                p.wa.special_income_limit.individual,
            ],
            default=0,
        )

        needs_based_income = min_(
            person("medicaid_ltss_needs_based_income", period),
            income,
        )
        non_needs_based_income = max_(income - needs_based_income, 0)
        delaware_disregard = min_(
            non_needs_based_income,
            p.de.income.general_disregard,
        )
        income_after_disregard = where(
            state == states.DE,
            max_(income - delaware_disregard, 0),
            income,
        )
        special_income_eligible = income_after_disregard <= special_income_limit

        medically_needy_expenses = person(
            "medicaid_ltss_medically_needy_expenses", period
        )
        cost_of_care = person("medicaid_ltss_cost_of_care", period)
        washington_institutional_mn_eligible = (setting == settings.INSTITUTIONAL) & (
            max_(income - medically_needy_expenses, 0) <= cost_of_care
        )
        washington_hcbs_mn_eligible = (setting == settings.HCBS) & (
            max_(
                income - medically_needy_expenses - cost_of_care,
                0,
            )
            <= p.wa.medically_needy.income_level
        )

        return ((pathway == pathways.SPECIAL_INCOME) & special_income_eligible) | (
            (pathway == pathways.INSTITUTIONAL_MEDICALLY_NEEDY)
            & (state == states.WA)
            & (washington_institutional_mn_eligible | washington_hcbs_mn_eligible)
        )
