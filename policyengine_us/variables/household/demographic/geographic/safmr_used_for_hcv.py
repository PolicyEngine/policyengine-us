from policyengine_us.model_api import *


class safmr_used_for_hcv(Variable):
    value_type = bool
    entity = Household
    label = "Small area fair market rent used for purposes of the Housing Choice Voucher Program"
    definition_period = YEAR

    def formula(household, period, parameters):
        # True wherever the model has a ZIP-level Small Area FMR for the
        # household (currently the four mandatory-SAFMR Texas metros).
        return household("small_area_fair_market_rent", period) > 0
