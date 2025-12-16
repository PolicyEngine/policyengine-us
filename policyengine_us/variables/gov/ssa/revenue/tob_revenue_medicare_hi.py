from policyengine_us.model_api import *


class tob_revenue_medicare_hi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue from Social Security benefit taxation credited to Medicare HI trust fund. "
        "Per IRC §86(d)(2), tax on the 'remaining portion' of SS benefits (above 50% of gross) goes to HI."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_2"

    def formula(tax_unit, period, parameters):
        """
        Calculate Medicare HI trust fund revenue per IRC §86(d)(2).

        Medicare HI receives tax on the 'remaining portion' of benefits -
        the amount of taxable SS above 50% of gross benefits.

        HI receives: total_tob - oasdi_portion
        """
        total_tob = tax_unit("tob_revenue_total", period)
        oasdi_portion = tax_unit("tob_revenue_oasdi", period)

        return total_tob - oasdi_portion
