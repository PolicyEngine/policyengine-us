from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.capital_gains_28_percent_rate_gain import (
    rate_gains_less_losses,
)


class schedule_d_unrecaptured_section_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unrecaptured section 1250 gain (Schedule D line 19)"
    unit = USD
    documentation = (
        "Schedule D line 19. Unrecaptured section 1250 gain entered as "
        "already reduced, as Schedule D line 19 reports it, plus line 18 of "
        "the Unrecaptured Section 1250 Gain Worksheet for the gain entered "
        "before losses: that gain less the amount by which collectibles "
        "loss, the net short-term capital loss and the long-term capital "
        "loss carried to the year exceed collectibles gain and section 1202 "
        "gain, if more than zero."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(6)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_6_A",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Unrecaptured Section 1250 Gain Worksheet—Line 19",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=13",
        ),
    ]

    def formula(tax_unit, period, parameters):
        reported = tax_unit("unrecaptured_section_1250_gain", period)
        # Worksheet line 13: 26 U.S.C. 1(h)(6)(A)(i).
        gain = tax_unit("unrecaptured_section_1250_gain_before_losses", period)
        # Line 17: the losses of section 1(h)(4)(B) in excess of the gains of
        # section 1(h)(4)(A), 26 U.S.C. 1(h)(6)(A)(ii). A 28-percent rate gain
        # means the gains exceed the losses, so there is no excess; reading
        # it keeps line 19 consistent with a Schedule D line 18 entered
        # directly.
        rate_gain = tax_unit("capital_gains_28_percent_rate_gain", period)
        excess_losses = where(
            rate_gain > 0, 0, max_(0, -rate_gains_less_losses(tax_unit, period))
        )
        return reported + max_(0, gain - excess_losses)
