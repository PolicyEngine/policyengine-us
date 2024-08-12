from policyengine_us.model_api import *


class safmr_used_for_hcv(Variable):
    value_type = bool
    entity = Household
    label = "Small area fair market rent used for purposes of the Housing Choice Voucher Program"
    definition_period = YEAR
