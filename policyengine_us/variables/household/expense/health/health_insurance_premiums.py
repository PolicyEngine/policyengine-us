from policyengine_us.model_api import *


class health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums"
    unit = USD
    definition_period = YEAR
    # Survey data put premiums here only for self-employed people under 65
    # without employer-sponsored coverage. CMS's premium per enrollee for
    # plans bought outside an employer is the closest series for them.
    uprating = "calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee"
    documentation = (
        "Annual person-paid health insurance premiums supplied directly as an "
        "input, excluding premiums paid through pretax payroll deductions and "
        "employer-paid premiums. Pretax payroll payments belong only in "
        "pre_tax_health_insurance_premiums; the two sets are disjoint and total "
        "person-paid premiums equal their sum. This direct non-pretax amount is "
        "an alternative to the applicable decomposed non-pretax inputs, not an "
        "additional expense."
    )
