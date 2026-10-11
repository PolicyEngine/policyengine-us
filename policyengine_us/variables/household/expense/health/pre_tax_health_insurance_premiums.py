from policyengine_us.model_api import *


class pre_tax_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Pre-tax health insurance premiums"
    unit = USD
    documentation = (
        "Health insurance premiums paid through pre-tax payroll deductions. "
        "This excludes Medicare Part B premiums and other post-tax medical "
        "out-of-pocket premiums. These are employees' shares of "
        "employer-sponsored insurance premiums, so they are uprated by CMS's "
        "employer-sponsored insurance premium per enrollee, holding the "
        "number of people covered per policy and the employee's share of the "
        "premium at their base-year levels."
    )
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
