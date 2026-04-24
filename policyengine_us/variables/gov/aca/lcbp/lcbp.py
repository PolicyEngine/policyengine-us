from policyengine_us.model_api import *


class lcbp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lowest-cost ACA bronze-plan cost"
    unit = USD
    definition_period = MONTH
    adds = ["lcbp_age_curve_amount_person", "lcbp_family_tier_amount"]
