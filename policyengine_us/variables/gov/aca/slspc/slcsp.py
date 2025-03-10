from policyengine_us.model_api import *


class slcsp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH
    adds = ["slcsp_age_curve_amount_person", "slcsp_family_tier_amount"]
