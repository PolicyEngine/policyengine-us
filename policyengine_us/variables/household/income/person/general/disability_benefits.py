from policyengine_us.model_api import *


class disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "disability benefits"
    unit = USD
    documentation = (
        "Disability benefits from employment (not Social Security), except for "
        "worker's compensation. Includes both the taxable and the tax-exempt part; "
        "see taxable_disability_benefits and tax_exempt_disability_benefits."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.employment_income"
