from policyengine_us.model_api import *


class other_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Other health insurance premiums"
    unit = USD
    definition_period = YEAR
    # The reported premiums in
    # health_insurance_premiums_without_medicare_part_b less modeled CHIP,
    # Medicaid and Marketplace premiums, so the same premium index.
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
    documentation = (
        "Person-level health insurance premiums not otherwise represented by "
        "modeled Marketplace, CHIP, Medicaid, Medicare Part A or Part B "
        "premiums, or the Part D IRMAA surcharge."
    )
