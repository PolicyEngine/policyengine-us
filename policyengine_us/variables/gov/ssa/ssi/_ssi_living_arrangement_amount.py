from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


def ssi_living_arrangement_amount(person, period, parameters, base_amount):
    """Adjust a federal benefit rate for the person's living arrangement."""
    p = parameters(period).gov.ssa.ssi.amount
    arrangement = person("ssi_federal_living_arrangement", period)

    # 20 CFR § 416.1131: One-third reduction for another person's
    # household. Applies to the applicable FBR (individual or couple
    # based on deeming).
    is_another_household = (
        arrangement == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
    )
    base_amount = where(
        is_another_household,
        base_amount * (1 - p.one_third_reduction_rate),
        base_amount,
    )

    # 42 USC § 1382(e)(1)(B), 20 CFR § 416.414: Medical treatment
    # facility, $30/month per person.
    is_medical_facility = (
        arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
    )
    return where(is_medical_facility, p.medical_facility, base_amount)
