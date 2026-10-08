from policyengine_us.model_api import *


class hi_capital_gain_for_alternative_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii capital gain for the alternative tax on capital gains"
    unit = USD
    documentation = (
        "Line 8 of the Hawaii Tax on Capital Gains Worksheet: the smaller of "
        "the net long-term capital gain and the net capital gain. Both come "
        "from federal Schedule D lines 15 and 16, which do not include "
        "qualified dividends."
    )
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=33"
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # Lines 2 and 4: federal Schedule D line 15, or Form 1040 line 7
        # if Schedule D is not required.
        net_lt_capital_gain = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        # Lines 5 and 7: federal Schedule D line 16 (lines 7 and 15 combined).
        net_st_capital_gain = add(tax_unit, period, ["short_term_capital_gains"])
        net_capital_gain = net_lt_capital_gain + net_st_capital_gain
        # Line 8. Line 10 stops the worksheet if this amount is zero or less.
        return max_(0, min_(net_lt_capital_gain, net_capital_gain))
