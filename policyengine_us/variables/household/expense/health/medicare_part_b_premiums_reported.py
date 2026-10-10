from policyengine_us.model_api import *


class medicare_part_b_premiums_reported(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums (reported)"
    definition_period = YEAR
    documentation = (
        "Annual reported person-paid Medicare Part B premiums excluding pretax "
        "payroll deductions and employer-paid premiums. Pretax payroll payments "
        "belong only in pre_tax_health_insurance_premiums. The pretax and non- "
        "pretax sets are disjoint; total person-paid premiums equal pretax "
        "payments plus the applicable non-pretax aggregate. A reported component "
        "must not be added again when already included in a broader premium "
        "input."
    )
    unit = USD
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
