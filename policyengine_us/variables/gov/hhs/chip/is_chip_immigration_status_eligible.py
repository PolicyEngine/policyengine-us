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
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf#page=17",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/sho26001.pdf#page=6",
        "https://www.nysenate.gov/legislation/laws/PBH/2511",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs
        # The federal test: citizens, qualified noncitizens exempt from or
        # past the five-year bar, and the lawfully residing option where the
        # state elected it in both CHIP and Medicaid. The routes below are
        # each state's own.
        federally_eligible = person(
            "is_federal_chip_immigration_status_eligible", period
        )
        status = person("immigration_status", period)
        state = person.household("state_code_str", period)
        age = person("age", period)
        # States that cover every child below an age limit regardless of
        # immigration status do so in CHIP as well as Medicaid.
        regardless = p.medicaid.eligibility.regardless_of_immigration_status
        child_eligible_regardless_of_status = age < regardless.child_age_limit[state]
        # Some states cover undocumented children in CHIP alone. These
        # children pass the Medicaid immigration test only through the
        # pregnancy term.
        undocumented = status == status.possible_values.UNDOCUMENTED
        undocumented_child = (
            undocumented
            & p.chip.undocumented.child[state].astype(bool)
            & (age < p.chip.child.max_age)
        )
        return (
            federally_eligible
            | child_eligible_regardless_of_status
            | undocumented_child
        )
