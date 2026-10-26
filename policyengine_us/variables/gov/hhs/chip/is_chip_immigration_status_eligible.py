from policyengine_us.model_api import *


class is_chip_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for CHIP due to immigration status"
    definition_period = YEAR
    # Separate CHIP covers citizens and qualified aliens who are exempt from or
    # past the five-year bar (8 USC 1611(a) and 1613). From October 1, 2026,
    # 42 USC 1397gg(e)(1)(R) applies the 1396b(v)(5) status limits to CHIP.
    # Under 42 USC 1397gg(e)(1)(Q), states that elected the lawfully residing
    # option for a group in both Medicaid and CHIP also cover that group.
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1611#a",
        "https://www.law.cornell.edu/uscode/text/8/1613",
        "https://www.law.cornell.edu/uscode/text/42/1397gg#e_1_Q",
        "https://www.law.cornell.edu/uscode/text/42/1397gg#e_1_R",
        "https://downloads.cms.gov/cmsgov/archived-downloads/smdl/downloads/sho10006.pdf#page=2",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/SHO-12-002.pdf#page=1",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho26001.pdf#page=6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs
        medicaid = p.medicaid.eligibility
        status = person("immigration_status", period)
        status_str = status.decode_to_str()
        citizen = status == status.possible_values.CITIZEN
        # CHIP shares the Medicaid qualified-alien statuses (narrowed by section
        # 71109 from October 2026) and the five-year bar (SHO #26-001).
        qualified_status = np.isin(status_str, medicaid.eligible_immigration_statuses)
        bar_exempt_status = np.isin(
            status_str, medicaid.bar_exempt_immigration_statuses
        )
        years_since_entry = person("years_since_us_entry", period)
        past_five_year_bar = years_since_entry >= medicaid.five_year_bar_years
        federally_eligible_status = citizen | (
            qualified_status & (bar_exempt_status | past_five_year_bar)
        )
        # The lawfully residing option reaches CHIP only for a group the state
        # elected in both CHIP and Medicaid.
        medicaid_option = medicaid.lawfully_residing
        chip_option = p.chip.lawfully_residing
        lawfully_residing = np.isin(status_str, medicaid_option.immigration_statuses)
        state = person.household("state_code_str", period)
        age = person("age", period)
        child = (
            chip_option.child[state].astype(bool)
            & medicaid_option.child[state].astype(bool)
            & (age < p.chip.child.max_age)
        )
        pregnant = (
            chip_option.pregnant[state].astype(bool)
            & medicaid_option.pregnant[state].astype(bool)
            & person("is_pregnant", period)
        )
        return federally_eligible_status | (lawfully_residing & (child | pregnant))
