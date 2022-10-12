from policyengine_us.model_api import *


class hud_max_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD max subsidy"
    unit = USD
    documentation = "Max subsidy for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1437a#b_2_B_5"

    def formula(spm_unit, period, parameters):
        ttp = spm_unit("hud_ttp", period)
        pha_payment_standard = spm_unit("pha_payment_standard", period)
        return max_(0, pha_payment_standard - ttp)
