from policyengine_us.model_api import *


class ny_real_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY real property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (e)(6)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # 606(e)(6)(A): through 2024 only one credit is allowed per household,
        # so every tax unit in the household other than the claimant gets
        # none. From 2025 (606(e)(6)(B)) every tax unit is its own claimant.
        potential = tax_unit("ny_real_property_tax_credit_potential", period)
        claimant = tax_unit("ny_real_property_tax_credit_claimant", period)
        return potential * claimant
