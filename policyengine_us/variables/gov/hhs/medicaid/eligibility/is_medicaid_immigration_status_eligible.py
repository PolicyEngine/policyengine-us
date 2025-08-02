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
        state = person.household("state_code_str", period)

        # Check if immigration status is in the federal baseline eligible list
        federal_eligible = np.isin(
            immigration_status_str, p.federal_eligible_immigration_statuses
        )

        # Check if immigration status is in state-specific extended coverage
        # Only states with extended coverage beyond federal requirements
        state_eligible = select(
            [
                state == "CA",
                state == "DC",
                state == "IL",
                state == "MA",
                state == "NY",
                state == "OR",
            ],
            [
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses.ca,
                ),
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses.dc,
                ),
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses.il,
                ),
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses.ma,
                ),
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses.ny,
                ),
                np.isin(
                    immigration_status_str,
                    p.state_extended_immigration_statuses["or_"],
                ),
            ],
            default=False,
        )

        return federal_eligible | state_eligible
