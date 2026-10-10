from policyengine_us.model_api import *


class pre_tax_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Pre-tax health insurance premiums"
    unit = USD
    documentation = (
        "Annual employee-paid health insurance premiums paid through pretax "
        "payroll deductions. Supply these only here: health_insurance_premiums "
        "and the applicable decomposed premium inputs exclude these payments. The "
        "pretax and non-pretax sets are disjoint; total employee-paid premiums "
        "equal their sum. Excludes employer-paid premiums."
    )
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
