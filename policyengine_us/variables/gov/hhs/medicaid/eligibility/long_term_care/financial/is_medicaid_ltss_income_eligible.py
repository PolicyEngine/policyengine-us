from policyengine_us.model_api import *


class is_medicaid_ltss_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS income threshold"
    definition_period = MONTH
    documentation = (
        "Tests only the income threshold for the selected modeled Medicaid "
        "LTSS financial pathway. Gross earned and unearned income and QIT "
        "deposits determine income after trust treatment; Washington medically "
        "needy expenses and cost of care are trusted inputs; this variable "
        "does not validate a trust, expense, service, or facility rate. The "
        "Washington institutional branch models the WAC 182-513-1395(4) "
        "payment threshold using income only: the excess-resources term in "
        "subsection (4)(a) is unmodeled, which makes this variable slightly "
        "lenient on its own, although the composite screen still applies "
        "the resource test. The three- or six-month spenddown process in "
        "subsection (5) and the WAC 182-515-1507 categorically needy route "
        "that bypasses the special income limit are also unmodeled. The "
        "Delaware special income limit is 250% of the SSI standard and "
        "applies only to nursing facility residents (DSSM 20100.2.2); "
        "Delaware's 100%-of-SSI standard for hospital stays is unmodeled, "
        "so the institutional setting should not be used for a hospitalized "
        "Delaware applicant. Delaware computes the $20 general exclusion "
        "from non-needs-based unearned income first, carries any unused "
        "part to earnings, "
        "deducts $65, and counts half the earnings remainder (DSSM "
        "20240.1 and 20240.3). There is one exclusion per couple budget. "
        "Applicants with a community spouse receive only the eligible "
        "$20 deduction (DSSM 20990)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.236",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/2026/06/2026-SSI-Related-Income-Standards-and-Medicare-Premiums.pdf#page=1",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=1",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=9",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
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
        income = person("medicaid_ltss_qit_adjusted_income", period)
        # The special income limit is zero outside the modeled states and
        # assistance-unit sizes; the SPECIAL_INCOME pathway gate below is what
        # keeps an unmodeled person from passing with zero income.
        special_income_limit = person("medicaid_ltss_special_income_limit", period)

        countable_income = person("medicaid_ltss_countable_income", period)
        special_income_eligible = countable_income <= special_income_limit

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
