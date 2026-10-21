from policyengine_us.model_api import *


class section_911_28_percent_rate_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "28-percent rate gain less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "28-percent rate gain for the regular tax rates. A taxpayer with a "
        "section 911 capital gain excess adds the excess to the losses "
        "subtracted in figuring 28-percent rate gain, which reduces the gain "
        "by the excess, but not below zero. Equals 28-percent rate gain for "
        "everyone else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(A)(iii)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A_iii",
        ),
        dict(
            title="26 U.S. Code § 1(h)(4)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_4",
        ),
        dict(
            title="2025 Form 1040 instructions, Foreign Earned Income Tax Worksheet—Line 16, footnote, modification 3",
            href="https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
        ),
    ]

    def formula(tax_unit, period, parameters):
        rate_gain = tax_unit("capital_gains_28_percent_rate_gain", period)
        excess = tax_unit("section_911_capital_gain_excess", period)
        return where(excess > 0, max_(0, rate_gain - excess), rate_gain)
