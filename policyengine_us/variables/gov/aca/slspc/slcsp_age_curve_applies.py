from policyengine_us.model_api import *


class slcsp_age_curve_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "ACA age curve applies, rather than family tier"
    unit = "bool"
    definition_period = MONTH
    subtracts = ["slcsp_family_tier_applies"]
