from policyengine_us.model_api import *


class la_oss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Louisiana Optional State Supplement (OSS)"
    documentation = (
        "Eligible if the person is aged, blind, or disabled and resides in a "
        "non-psychiatric Medicaid long-term care facility (federal Code D living "
        "arrangement: nursing facility or ICF/IID) in Louisiana. We don't track "
        "Medicare SNF coverage, MAGI vs. non-MAGI Medicaid pathway, transfer-of-"
        "resource or home-equity penalties, temporary (<=3 month) institutional "
        "stays, or HCBS waiver enrollment at the moment, so the corresponding "
        "regulatory exclusions are not applied."
    )
    definition_period = MONTH
    defined_for = StateCode.LA
    reference = (
        "https://ldh.la.gov/assets/medicaid/MedicaidEligibilityPolicy/J-0000.pdf#page=2",
        "https://ldh.la.gov/assets/medicaid/MedicaidEligibilityPolicy/H-800.pdf#page=9",
    )

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        in_ltc_facility = person("is_in_medicaid_facility", period)
        return aged_blind_disabled & in_ltc_facility
