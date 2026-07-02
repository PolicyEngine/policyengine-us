from policyengine_us.model_api import *


class other_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Other health insurance premiums"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
    documentation = (
        "Person-level health insurance premiums not otherwise represented by "
        "modeled Marketplace, CHIP, Medicaid, Medicare Part A or Part B "
        "premiums, or the Part D IRMAA surcharge."
    )
