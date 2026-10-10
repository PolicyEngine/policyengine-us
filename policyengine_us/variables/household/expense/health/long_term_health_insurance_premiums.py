from policyengine_us.model_api import *


class long_term_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Long-term health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual person-paid long-term care insurance premiums excluding pretax "
        "payroll deductions and employer-paid premiums. Pretax payroll payments "
        "belong only in pre_tax_health_insurance_premiums. The pretax and non- "
        "pretax sets are disjoint; total person-paid premiums equal pretax "
        "payments plus the applicable non-pretax aggregate. This component must "
        "be counted only once when included in a broader premium input."
    )
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
