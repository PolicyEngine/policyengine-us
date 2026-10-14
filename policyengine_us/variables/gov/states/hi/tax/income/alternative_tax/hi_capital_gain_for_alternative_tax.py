from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.filer_schedule_d_lines import (
    filer_schedule_d_lines,
)


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
        # Lines 2 and 4: the head and spouse's Schedule D line 15, including
        # their capital gain distributions, each floored at zero. Dependents'
        # amounts belong on their own returns.
        lines = filer_schedule_d_lines(tax_unit, period)
        # Lines 5 and 7: combine the filers' person-level short- and long-term
        # gains, as this worksheet does when deriving Schedule D line 16.
        net_capital_gain = lines.line_15 + lines.line_7
        # Line 8. Line 10 stops the worksheet if this amount is zero or less.
        return max_(0, min_(lines.line_15, net_capital_gain))
