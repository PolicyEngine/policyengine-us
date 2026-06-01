from policyengine_us.model_api import *


class medicaid_slcsp_family_tier_person_share(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid SLCSP family-tier person share"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        base_cost = tax_unit.household("slcsp_age_0", period.first_month)
        multiplier = tax_unit("medicaid_slcsp_family_tier_multiplier", period)
        tax_unit_size = tax_unit("tax_unit_size", period)

        return np.divide(
            base_cost * multiplier,
            tax_unit_size,
            out=np.zeros_like(base_cost),
            where=tax_unit_size > 0,
        )
