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
        medicaid_member_count = add(tax_unit, period, ["medicaid_enrolled"])

        return np.divide(
            base_cost * multiplier,
            medicaid_member_count,
            out=np.zeros_like(base_cost),
            where=medicaid_member_count > 0,
        )
