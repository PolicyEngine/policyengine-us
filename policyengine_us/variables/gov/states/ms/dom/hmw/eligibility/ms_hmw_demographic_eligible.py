from policyengine_us.model_api import *


class ms_hmw_demographic_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Healthier Mississippi Waiver demographic eligibility rules"
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=9",
        "https://medicaid.ms.gov/wp-content/uploads/2026/02/HMW-Fact-Sheet-2026.pdf#page=1",
    )

    def formula(person, period, parameters):
        return (
            person("is_ssi_aged_blind_disabled", period)
            & ~person("is_pregnant", period)
            & ~person("is_in_medicaid_facility", period.first_month)
        )
