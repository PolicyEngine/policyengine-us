from policyengine_us.model_api import *


class il_hbi_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for Illinois HBI"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
    )
    # Illinois Health Benefits for Immigrants (HBI) covers residents who are not
    # eligible for federal Medicaid due to their immigration status.

    def formula(person, period, parameters):
        # Eligible for HBI if NOT eligible for federal Medicaid
        # due to immigration status
        federal_eligible = person(
            "is_medicaid_immigration_status_eligible", period
        )
        return ~federal_eligible
