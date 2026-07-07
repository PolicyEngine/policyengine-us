from policyengine_us.model_api import *


class nyc_school_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Computed with a formula rather than an adds list so that household
        # output surfaces only the final credit; the fixed and rate-reduction
        # pieces are components of one credit, not separate credits (#8938).
        return add(
            tax_unit,
            period,
            [
                "nyc_school_tax_credit_fixed_amount",
                "nyc_school_tax_credit_rate_reduction_amount",
            ],
        )
