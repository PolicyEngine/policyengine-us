from policyengine_us.model_api import *


class spm_unit_health_insurance_premiums(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Health insurance premium expenses for an SPM unit, combining a "
        "data-imputed residual premium component with modeled premium "
        "components that can respond to policy reforms."
    )

    def formula(spm_unit, period, parameters):
        return add(
            spm_unit,
            period,
            [
                "health_insurance_premium_residual",
                "chip_premium",
                "medicaid_premium",
                "marketplace_net_premium",
                "income_adjusted_part_b_premium",
            ],
        )
