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
        "equal their sum. Excludes employer-paid premiums, Medicare Part B "
        "premiums and other post-tax medical premiums. These are employees' shares of "
        "employer-sponsored insurance premiums, so they are uprated by CMS's "
        "employer-sponsored insurance premium per enrollee, holding the "
        "number of people covered per policy and the employee's share of the "
        "premium at their base-year levels."
    )
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
