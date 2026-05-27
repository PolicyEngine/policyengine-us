from policyengine_us.model_api import *


class spm_unit_health_insurance_premiums(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Health insurance premium expenses for an SPM unit, combining a "
        "data-imputed other premium component with modeled premium components "
        "that can respond to policy reforms, including Medicare premiums "
        "paid out of pocket."
    )

    adds = [
        "other_health_insurance_premiums",
        "chip_premium",
        "medicaid_premium",
        "marketplace_net_premium",
        "medicare_part_a_premium",
        "medicare_part_b_premium",
        "income_adjusted_part_d_premium_surcharge",
    ]
