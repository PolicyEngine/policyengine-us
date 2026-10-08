from policyengine_us.model_api import *


class medicaid_ltss_assistance_unit_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid LTSS assistance unit size"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Delaware's assistance unit is derived from the spouses' service "
        "requests or receipt, location, and completed months together in "
        "the same institutional facility (DSSM 20810). A two-person marital "
        "unit requesting or receiving services in the same facility must "
        "use couple budgeting until six completed months there; at six "
        "months the couple's reported "
        "medicaid_ltss_de_post_six_month_budget_election selects individual "
        "or couple budgeting. When that election is NOT_SUPPLIED, the "
        "model uses whichever budget allows more spouses to pass both "
        "income and resource thresholds, choosing individual budgets in "
        "a tie. Outside that same-facility post-six-month window, a "
        "reported election has no effect. Both spouses receive the same "
        "budget. HCBS "
        "spouses requesting or receiving services at the same address use "
        "couple standards without a six-month election. Other Delaware "
        "applicants use an individual budget. This derives the budgeting "
        "unit independently of whether a financial pathway is modeled. "
        "Outside Delaware, supply the separate "
        "medicaid_ltss_non_delaware_assistance_unit_size input: use two only "
        "where both spouses are budgeted as a couple, including Texas "
        "spouses in the same institutional setting, and one for an "
        "individual applicant. The outside-Delaware default zero and "
        "unsupported sizes fail closed. Income and resources are supplied "
        "for each person and combined internally for a couple budget."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.602",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/g-6100-institutional-eligibility-budgets",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-436",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67",
    )

    def formula_2026_01_01(person, period, parameters):
        state = person.household("state_code", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        fbr = parameters(period).gov.ssa.ssi.amount
        resources_limit = parameters(period).gov.ssa.ssi.eligibility.resources.limit

        is_couple = person.marital_unit.nb_persons() == 2
        same_facility = is_couple & person.marital_unit(
            "medicaid_ltss_spouses_requesting_or_receiving_institutional_services_in_same_facility",
            period,
        )
        months_together = person.marital_unit(
            "medicaid_ltss_spouses_months_in_same_institutional_facility", period
        )
        same_address_hcbs = is_couple & person.marital_unit(
            "medicaid_ltss_spouses_requesting_or_receiving_hcbs_at_same_address",
            period,
        )

        # The fallback compares both candidate budgets without reading any
        # output dependent on the elected unit, avoiding a calculation cycle.
        individual_resources = person(
            "medicaid_ltss_individual_countable_resources", period
        )
        individual_income = person("medicaid_ltss_individual_countable_income", period)
        individual_passes = (
            individual_income <= p.de.special_income_limit.rate * fbr.individual
        ) & (individual_resources <= resources_limit.individual)
        individual_eligible_spouses = person.marital_unit.sum(individual_passes)
        couple_income = person("medicaid_ltss_couple_countable_income", period)
        couple_resources = person.marital_unit.sum(individual_resources)
        couple_passes = (
            couple_income <= p.de.special_income_limit.rate * fbr.couple
        ) & (couple_resources <= resources_limit.couple)
        couple_eligible_spouses = 2 * couple_passes
        favorable_couple_budget = couple_eligible_spouses > individual_eligible_spouses
        election = person.marital_unit(
            "medicaid_ltss_de_post_six_month_budget_election", period
        )
        election_values = election.possible_values
        elected_couple_budget = select(
            [
                election == election_values.INDIVIDUAL,
                election == election_values.COUPLE,
            ],
            [False, True],
            default=favorable_couple_budget,
        )
        # DSSM 20810 allows an election only after six completed months in
        # the same facility; mandatory institutional and HCBS units prevail.
        institutional_couple = same_facility & (
            (months_together < 6) | elected_couple_budget
        )
        delaware_unit = where(same_address_hcbs | institutional_couple, 2, 1)
        return where(
            state == state.possible_values.DE,
            delaware_unit,
            person("medicaid_ltss_non_delaware_assistance_unit_size", period),
        )
