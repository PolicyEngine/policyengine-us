from policyengine_us.model_api import *


def rate_gains_less_losses(tax_unit, period):
    """Collectibles gain and section 1202 gain entered before netting, less
    the losses netted against them (26 U.S.C. 1(h)(4)(A) less 1(h)(4)(B)),
    which can be negative.

    Lines 1 to 6 of the 28% Rate Gain Worksheet combined: collectibles gain or
    (loss) (lines 1, 3 and 4), section 1202 gain (line 2), the long-term
    capital loss carryover (line 5) and the Schedule D line 7 loss (line 6).
    The same amount is lines 14 to 16 of the Unrecaptured Section 1250 Gain
    Worksheet combined. Amounts entered already netted, as Schedule D lines
    18 and 19 report them, are not part of it.
    """
    # Collectibles gain or (loss); a net collectibles loss is negative.
    collectibles = add(tax_unit, period, ["collectibles_gain_or_loss"])
    section_1202_gain = max_(0, add(tax_unit, period, ["section_1202_gain"]))
    # 26 U.S.C. 1222(6), the same net short-term capital loss net_capital_gain
    # subtracts: Schedule D line 7, if a loss.
    net_short_term_capital_loss = max_(
        0, -add(tax_unit, period, ["short_term_capital_gains"])
    )
    carryover = max_(0, add(tax_unit, period, ["long_term_capital_loss_carryover"]))
    return collectibles + section_1202_gain - net_short_term_capital_loss - carryover


class capital_gains_28_percent_rate_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "28-percent rate gain"
    unit = USD
    documentation = (
        "Schedule D line 18. The collectibles and section 1202 amounts "
        "entered as already netted, as Schedule D line 18 reports them, plus "
        "line 7 of the 28% Rate Gain Worksheet for the amounts entered "
        "before netting: collectibles gain and section 1202 gain less "
        "collectibles loss, the net short-term capital loss and the "
        "long-term capital loss carried to the year, if more than zero."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(4)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_4",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), 28% Rate Gain Worksheet—Line 18",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=11",
        ),
    ]

    def formula(tax_unit, period, parameters):
        reported = add(
            tax_unit,
            period,
            [
                "long_term_capital_gains_on_collectibles",
                "long_term_capital_gains_on_small_business_stock",
            ],
        )
        return reported + max_(0, rate_gains_less_losses(tax_unit, period))
