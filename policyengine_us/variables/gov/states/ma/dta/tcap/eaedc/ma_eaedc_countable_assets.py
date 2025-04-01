from policyengine_us.model_api import *


class ma_eaedc_countable_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC countable assets"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA

    adds = "gov.states.ma.dta.tcap.eaedc.assets.sources"
