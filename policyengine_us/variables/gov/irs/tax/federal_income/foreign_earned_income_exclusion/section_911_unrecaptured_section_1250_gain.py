from policyengine_us.model_api import *


class section_911_unrecaptured_section_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unrecaptured section 1250 gain less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "Unrecaptured section 1250 gain for the regular tax rates. A taxpayer "
        "with a section 911 capital gain excess adds the excess to the losses "
        "of section 1(h)(4)(B). The part of the excess that the 28-percent "
        "rate gain does not absorb then reduces unrecaptured section 1250 "
        "gain, but not below zero. Equals unrecaptured section 1250 gain for "
        "everyone else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(A)(iii)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A_iii",
        ),
        dict(
            title="26 U.S. Code § 1(h)(6)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_6_A",
        ),
        dict(
            title="2025 Form 1040 instructions, Foreign Earned Income Tax Worksheet—Line 16, footnote, modification 4",
            href="https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
        ),
    ]

    def formula(tax_unit, period, parameters):
        unrecaptured_gain = tax_unit("unrecaptured_section_1250_gain", period)
        rate_gain = tax_unit("capital_gains_28_percent_rate_gain", period)
        excess = tax_unit("section_911_capital_gain_excess", period)
        excess_over_rate_gain = max_(0, excess - rate_gain)
        return where(
            excess > 0,
            max_(0, unrecaptured_gain - excess_over_rate_gain),
            unrecaptured_gain,
        )
