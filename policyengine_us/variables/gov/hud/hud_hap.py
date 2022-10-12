from policyengine_us.model_api import *


class hud_hap(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD housing assistance payment"
    unit = USD
    documentation = "HUD housing assistance payment"
    definition_period = YEAR
    reference = "https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf"

    def formula(spm_unit, period, parameters):
        max_subsidy = spm_unit("hud_max_subsidy", period)
        ttp = spm_unit("hud_ttp", period)
        gross_rent = spm_unit("hud_gross_rent", period)
        rent_minus_ttp = max_(0, gross_rent - ttp)
        return min_(max_subsidy, rent_minus_ttp)
