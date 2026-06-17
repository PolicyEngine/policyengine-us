from policyengine_us.model_api import *


class basic_health_program_family_tier_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic Health Program family-tier reference premium"
    unit = USD
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        return tax_unit.household("slcsp_age_0", period) * tax_unit(
            "basic_health_program_family_tier_multiplier", period
        )
