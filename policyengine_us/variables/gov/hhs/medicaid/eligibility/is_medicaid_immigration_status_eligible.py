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
        "https://www.nysenate.gov/legislation/laws/SOS/366",
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXVII/Chapter118E/Section16D",
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
        # Some states cover undocumented immigrants only during pregnancy and
        # the postpartum period, or only at age 65 or older.
        covers_pregnancy = p.undocumented.pregnant[state].astype(bool)
        covers_aged = p.undocumented.aged[state].astype(bool)
        # The pregnancy term reuses the Medicaid pregnancy category's test, so
        # this term and that category end on the same day by design. The test
        # counts days since the pregnancy ended. Massachusetts continues
        # coverage "to the end of the month in which the 12-month period ends"
        # (130 CMR 505.002(D)(4)), so the model's day count ends before that
        # continuation does.
        pregnant = person("is_pregnant_for_medicaid_nfc", period)
        aged = person("is_ssi_aged", period)
        undocumented_eligible = undocumented & (
            state_covers_undocumented
            | (covers_pregnancy & pregnant)
            | (covers_aged & aged)
        )

        # Some states cover every child below an age limit with state funds,
        # whatever the child's immigration status.
        age = person("age", period)
        child_age_limit = p.regardless_of_immigration_status.child_age_limit[state]
        child_eligible_regardless_of_status = age < child_age_limit

        ca_eligible_regardless_of_immigration_status = person(
            "is_ca_medicaid_immigration_status_eligible", period
        )
        # New York covers some statuses outside the federal test with state
        # funds.
        ny_state_funded_eligible = person(
            "is_ny_medicaid_immigration_status_eligible", period
        )

        return (
            federally_eligible
            | undocumented_eligible
            | child_eligible_regardless_of_status
            | ca_eligible_regardless_of_immigration_status
            | ny_state_funded_eligible
        )
