from policyengine_us.model_api import *


class hud_ttp(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD total tenant payment"
    unit = USD
    documentation = "Total Tenant Payment"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.628"

    def formula(spm_unit, period, parameters):
        # Calculated as the maximum of four values.
        return max_.reduce(
            [
                spm_unit("hud_ttp_income_share", period),
                spm_unit("hud_ttp_adjusted_income_share", period),
                spm_unit("housing_designated_welfare", period),
                spm_unit("hud_minimum_rent", period),
            ]
        )
