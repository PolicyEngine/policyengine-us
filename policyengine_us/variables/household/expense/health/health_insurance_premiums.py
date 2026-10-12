from policyengine_us.model_api import *


class health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
    documentation = (
        "Person-level health insurance premiums supplied directly as an input. "
        "SPM MOOP and statutory medical expense definitions use decomposed "
        "premium aggregates."
    )
