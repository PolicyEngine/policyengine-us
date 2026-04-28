from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class la_oss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Louisiana Optional State Supplement (OSS)"
    documentation = (
        "Eligible if the person is aged, blind, or disabled and resides in a "
        "non-psychiatric Medicaid long-term care facility (federal Code D living "
        "arrangement: nursing facility or ICF/IID) in Louisiana "
    )
    definition_period = MONTH
    defined_for = StateCode.LA
    reference = (
        "https://ldh.la.gov/assets/medicaid/MedicaidEligibilityPolicy/J-0000.pdf#page=2",
        "https://ldh.la.gov/assets/medicaid/MedicaidEligibilityPolicy/H-800.pdf#page=9",
    )

    def formula(person, period, parameters):
        # Tie eligibility to the same federal SSI living-arrangement enum
        # that triggers the $30 institutional FBR. `is_ssi_eligible` covers
        # the categorical (aged/blind/disabled), resource, and nonfinancial
        # (immigration/residency) gates without imposing the federal income
        # test — which is what we want, since LA OSS also reaches non-SSI
        # LTC residents whose countable income sits above the FBR but below
        # the PNA.
        ssi_eligible = person("is_ssi_eligible", period)
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        return ssi_eligible & in_medical_facility
