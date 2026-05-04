from policyengine_us.model_api import *


class spm_unit_medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit medical out-of-pocket expenses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Total medical out-of-pocket expenses at the SPM unit level, "
        "combining health insurance premiums with non-premium medical "
        "expenses. Health insurance premiums include other health insurance "
        "premiums plus modeled Marketplace, CHIP, Medicaid, and Medicare Part "
        "B premiums. Non-premium expenses include other medical expenses and "
        "over-the-counter health expenses."
    )

    adds = [
        "spm_unit_health_insurance_premiums",
        "spm_unit_non_premium_medical_out_of_pocket_expenses",
    ]
