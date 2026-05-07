from policyengine_us.model_api import *


class is_basic_health_program_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Basic Health Program coverage"
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/basic-health-program",
        "https://mn.gov/dhs/people-we-serve/adults/health-care/health-care-programs/programs-and-services/minnesotacare.jsp",
        "https://info.nystateofhealth.ny.gov/EssentialPlan",
        "https://www.oregon.gov/oha/ohp/pages/bridge.aspx",
        "https://hbx.dc.gov/page/basic-health-plan",
    )
    documentation = """
    First slice of Basic Health Program modeling.

    This models the adult public-coverage path that substitutes for Marketplace
    coverage in states with BHP-like programs. It uses one common program path
    for MinnesotaCare, New York's Essential Plan, Oregon OHP Bridge, and DC's
    Healthy DC Plan so ACA interactions can be modeled consistently.

    Child-specific and funding-mechanism nuances remain a follow-up.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.basic_health_program.eligibility

        state = person.household("state_code_str", period)
        in_effect = np.isin(state, p.active_states)

        age = person("age", period)
        age_eligible = (age >= p.min_age) & (age < p.max_age)

        medicaid_eligible = person("is_medicaid_eligible", period)
        chip_eligible = person("is_chip_eligible", period)
        esi_eligible = person("is_aca_eshi_eligible", period)
        medicare_eligible = person("is_medicare_eligible", period)
        immigration_eligible = person("is_aca_ptc_immigration_status_eligible", period)

        income_level = person("medicaid_income_level", period)
        expanded_limit_state = np.isin(state, p.expanded_income_limit_states)
        income_limit = where(
            expanded_limit_state,
            p.expanded_income_limit,
            p.income_limit,
        )
        # 42 USC 18051(b)(2)(B): BHP covers income above 133% FPL. The
        # ~medicaid_eligible guard alone is insufficient for non-expansion
        # states (where Medicaid may cut off below 133% FPL), so enforce
        # the statutory floor explicitly. Citizens below 133% are in
        # Medicaid in expansion states or the coverage gap otherwise.
        in_income_range = (income_level >= p.income_floor) & (
            income_level <= income_limit
        )

        return (
            in_effect
            & age_eligible
            & immigration_eligible
            & ~medicaid_eligible
            & ~chip_eligible
            & ~esi_eligible
            & ~medicare_eligible
            & in_income_range
        )
