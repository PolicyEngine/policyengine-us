from policyengine_us.model_api import *


class health_insurance_premiums_without_medicare_part_b(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums without Medicare Part B premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual person-paid health insurance premiums excluding Medicare Part B, "
        "pretax payroll deductions, and employer-paid premiums. Pretax payroll "
        "payments belong only in pre_tax_health_insurance_premiums. The pretax "
        "and non-pretax sets are disjoint; total person-paid premiums equal "
        "pretax payments plus the applicable non-pretax aggregate. This input is "
        "the non-Medicare component of the medical expense premium aggregate."
    )
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
