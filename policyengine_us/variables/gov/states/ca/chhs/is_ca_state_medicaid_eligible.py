from policyengine_us.model_api import *


class is_ca_state_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for California state-funded Medicaid"
    definition_period = YEAR
    reference = [
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/Medi-Cal-for-All.aspx",
        "https://www.chcf.org/publication/medi-cal-expansion-undocumented-adults/",
    ]
    defined_for = StateCode.CA


    def formula(person, period, parameters):
        # Check if person meets federal Medicaid category requirements (age and income)
        category = person("medicaid_category", period)
        categorically_eligible = category != category.possible_values.NONE

        # Check if person is NOT eligible for federal Medicaid due to immigration status
        not_federally_eligible = ~person(
            "is_medicaid_immigration_status_eligible", period
        )

        # Get state
        state = person.household("state_code_str", period)
        is_ca = state == "CA"

        # Check age-specific eligibility for CA state-funded program (regardless of immigration status)
        is_child_eligible = person(
            "is_ca_state_medicaid_child_eligible", period
        )
        is_young_adult_eligible = person(
            "is_ca_state_medicaid_young_adult_eligible", period
        )
        is_adult_eligible = person(
            "is_ca_state_medicaid_adult_eligible", period
        )
        is_older_adult_eligible = person(
            "is_ca_state_medicaid_older_adult_eligible", period
        )

        age_eligible = (
            is_child_eligible
            | is_young_adult_eligible
            | is_adult_eligible
            | is_older_adult_eligible
        )

        return (
            is_ca
            & categorically_eligible
            & not_federally_eligible
            & age_eligible
        )
