from policyengine_us.model_api import *


class health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums"
    unit = USD
    definition_period = YEAR
    # Survey data put premiums here only for self-employed people under 65
    # without employer-sponsored coverage, who buy plans directly.
    uprating = "calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee"
    documentation = (
        "Person-level health insurance premiums supplied directly as an input. "
        "SPM MOOP and statutory medical expense definitions use decomposed "
        "premium aggregates."
    )
