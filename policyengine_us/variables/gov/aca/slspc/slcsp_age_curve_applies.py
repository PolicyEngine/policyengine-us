from policyengine_us.model_api import *


class slcsp_age_curve_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "ACA age curve applies, rather than family tier"
    definition_period = MONTH

    def formula(tax_unit, period, parameters):
        family_tier_applies = tax_unit("slcsp_family_tier_applies", period)
        return ~family_tier_applies
