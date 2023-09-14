from policyengine_us.model_api import *


class wv_home_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia home value"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
