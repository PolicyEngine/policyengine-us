from policyengine_us.model_api import *
import numpy as np


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

        # Check if immigration status is in the eligible list for federal Medicaid
        # State-specific coverage for undocumented immigrants is now handled
        # by separate state program variables (e.g., is_ca_state_medicaid_eligible)
        eligible_immigration_status = np.isin(
            immigration_status_str, p.eligible_immigration_statuses
        )

        return eligible_immigration_status
