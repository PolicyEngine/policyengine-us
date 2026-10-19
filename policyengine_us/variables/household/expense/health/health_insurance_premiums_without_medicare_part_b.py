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
    # Survey data carry the person's reported premiums here (CPS ASEC
    # PHIP_VAL), most of them paid by people with employer-sponsored
    # coverage. They follow the same premium index as
    # pre_tax_health_insurance_premiums, so a premium moved from one input
    # to the other grows the same way.
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
