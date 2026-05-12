from policyengine_us.model_api import *


class pre_tax_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Pre-tax health insurance premiums"
    unit = USD
    documentation = (
        "Health insurance premiums paid through pre-tax payroll deductions. "
        "This excludes Medicare Part B premiums and other post-tax medical "
        "out-of-pocket premiums."
    )
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
