from policyengine_us.model_api import *


class is_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for Medicaid due to immigration status"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v_4_A",
        "https://www.law.cornell.edu/uscode/text/8/1641",
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1613&num=0&edition=prelim",
        "https://www.kff.org/racial-equity-and-health-policy/fact-sheet/key-facts-on-health-coverage-of-immigrants/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility
        immigration_status = person("immigration_status", period)
        # The federal test: citizens, qualified noncitizens exempt from or past the
        # five-year bar, and the lawfully residing option in 42 USC 1396b(v)(4).
        federally_eligible = person(
            "is_federal_medicaid_immigration_status_eligible", period
        )

        # Special handling for undocumented immigrants in states that cover them
        undocumented = (
            immigration_status == immigration_status.possible_values.UNDOCUMENTED
        )
        state = person.household("state_code_str", period)
        state_covers_undocumented = p.undocumented_immigrant[state].astype(bool)
        undocumented_eligible = undocumented & state_covers_undocumented

        ca_eligible_regardless_of_immigration_status = person(
            "is_ca_medicaid_immigration_status_eligible", period
        )

        return (
            federally_eligible
            | undocumented_eligible
            | ca_eligible_regardless_of_immigration_status
        )
