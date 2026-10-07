from policyengine_us.model_api import *


class net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain"
    unit = USD
    documentation = (
        "The excess of net long-term capital gain over net short-term capital "
        "loss, reduced by any part of it elected as investment income, plus "
        "qualified dividends not elected as investment income (the "
        'definition of "net capital gain" which applies to 26 U.S.C. § 1(h), '
        "from § 1(h)(2) and § 1(h)(11))."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 1222(11)",
            href="https://www.law.cornell.edu/uscode/text/26/1222#11",
        ),
        dict(
            title="26 U.S. Code § 1(h)(2)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_2",
        ),
        dict(
            title="26 U.S. Code § 1(h)(11)(A), (D)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_11",
        ),
        dict(
            title="2025 Form 4952, line 4g instructions",
            href="https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=4",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Capital gain distributions, including those reported without
        # Schedule D (Form 1040 line 7 with the box checked), are long-term
        # capital gains under IRC 852(b)(3)(B). Only the head's and spouse's
        # gains belong on this return, as on their Form 4952.
        long_term_gain = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains"]
        ) + tax_unit("form_4952_capital_gain_distributions", period)
        short_term_loss = max_(
            0, -tax_unit_non_dep_add(tax_unit, period, ["short_term_capital_gains"])
        )
        # 26 U.S.C. 1222(11), determined without regard to section 1(h)(11).
        gain = max_(0, long_term_gain - short_term_loss)
        # Form 4952 line 4g: the net capital gain and qualified dividends
        # elected to be included in investment income (26 U.S.C. 163(d)(4)(B)),
        # the same effective amount the investment interest deduction uses.
        # The amount "is generally treated as being attributable first to net
        # capital gain ... and then to qualified dividends" (line 4g
        # instructions): first to Form 4952 line 4e (Schedule D Tax Worksheet
        # line 8), then to qualified dividends (worksheet line 5). Section
        # 1(h)(2) removes the gain part, the amount taken into account under
        # 163(d)(4)(B)(iii); section 1(h)(11)(D)(i) removes the rest from
        # qualified dividend income.
        election = tax_unit("form_4952_elected_investment_income", period)
        gain_elected = min_(election, tax_unit("form_4952_net_capital_gain", period))
        dividends_elected = election - gain_elected
        qualified_dividends = max_(
            0,
            tax_unit("form_4952_qualified_dividends", period) - dividends_elected,
        )
        return max_(0, gain - gain_elected) + qualified_dividends
