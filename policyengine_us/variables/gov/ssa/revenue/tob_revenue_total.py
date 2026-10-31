from policyengine_us.model_api import *


class tob_revenue_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Total trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue from taxation of Social Security benefits using "
        "branching methodology per 42 U.S.C. 401 note. The total and its "
        "OASDI and Medicare HI shares are signed: negative unit differences "
        "are retained for aggregation."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/401"

    def formula(tax_unit, period, parameters):
        """
        Calculate total trust fund revenue using branching + neutralization.

        This isolates the tax impact of including taxable SS in AGI by
        comparing tax with and without taxable SS.
        """
        # Calculate income tax WITH taxable SS
        income_tax_with_ss = tax_unit("income_tax", period)
        income_tax_without_ss = tax_unit("income_tax_without_social_security", period)

        return income_tax_with_ss - income_tax_without_ss
