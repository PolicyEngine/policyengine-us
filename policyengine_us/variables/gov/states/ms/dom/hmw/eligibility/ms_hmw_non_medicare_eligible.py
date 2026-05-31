from policyengine_us.model_api import *


class ms_hmw_non_medicare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Healthier Mississippi Waiver Medicare exclusion"
    documentation = (
        "The Healthier Mississippi Waiver excludes people eligible for "
        "Medicare. Use Medicare eligibility rather than Medicare enrollment "
        "so Medicaid eligibility does not depend on modeled Medicare take-up."
    )
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2024/09/Healthier-Mississippi-Extension.pdf#page=9",
        "https://medicaid.ms.gov/wp-content/uploads/2024/04/20240403_MES_Gainwell_PRP-101_Member-Coverage-Description-Job_Aid_v0.1.pdf#page=5",
        "https://medicaid.ms.gov/wp-content/uploads/2026/02/HMW-Fact-Sheet-2026.pdf#page=1",
    )

    def formula(person, period, parameters):
        return ~person("is_medicare_eligible", period)
