from policyengine_us.model_api import *


class is_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for Medicaid due to immigration status"
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/8/1641",
        "https://www.kff.org/racial-equity-and-health-policy/fact-sheet/key-facts-on-health-coverage-of-immigrants/",
    ]

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        # Check if immigration status is in the eligible list
        eligible_immigration_status = np.isin(
            immigration_status_str, p.eligible_immigration_statuses
        )

        # Special handling for undocumented immigrants in states that cover them
        undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        state = person.household("state_code_str", period)
        state_covers_undocumented = p.undocumented_immigrant[state].astype(
            bool
        )
        undocumented_eligible = undocumented & state_covers_undocumented

        return eligible_immigration_status | undocumented_eligible
