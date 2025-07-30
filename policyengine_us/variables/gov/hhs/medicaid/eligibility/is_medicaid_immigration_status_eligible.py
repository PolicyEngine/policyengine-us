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
        # Handle states with no extended coverage using getattr with None default
        state_code_lower = state.lower()
        if state_code_lower == "or":
            state_code_lower = "or_"

        state_extended_param = getattr(
            p.state_extended_immigration_statuses, state_code_lower, None
        )

        state_eligible = where(
            state_extended_param is not None,
            np.isin(immigration_status_str, state_extended_param),
            False,
        )

        return federal_eligible | state_eligible
