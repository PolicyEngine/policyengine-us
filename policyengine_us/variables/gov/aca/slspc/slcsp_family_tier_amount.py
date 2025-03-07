from policyengine_us.model_api import *


class slcsp_family_tier_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA family tier premium amount"
    unit = USD
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        # Get the base premium
        base_cost = tax_unit.household("slcsp_age_0", period)

        # Get the family tier multiplier based on composition
        family_tier_multiplier = tax_unit(
            "slcsp_family_tier_multiplier", period
        )

        # Calculate the total premium amount for the family tier
        return base_cost * family_tier_multiplier
