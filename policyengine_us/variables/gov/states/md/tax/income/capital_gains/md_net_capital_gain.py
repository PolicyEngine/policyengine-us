from policyengine_us.model_api import *


class md_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland net capital gain included in Maryland adjusted gross income"
    unit = USD
    documentation = (
        "Net capital gain as defined and determined under the Internal "
        "Revenue Code, 26 U.S.C. 1222(11): the excess of the net long-term "
        "capital gain over the net short-term capital loss. This is the "
        "amount included in Maryland adjusted gross income that Md. Code, "
        "Tax-General 10-105(a)(3)(i)2 taxes at an additional 2%, before the "
        "excepted assets of (a)(3)(ii). Form 502CG line 1. A net short-term "
        "capital gain is not part of it, and neither are qualified dividends, "
        "which section 1(h)(11) adds only for section 1(h). Only the head's "
        "and spouse's gains count; a tax unit dependent's gains are on the "
        "dependent's own return."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="Md. Code, Tax-General § 10-105(a)(3)",
            href="https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-105&enactments=false",
        ),
        dict(
            title="26 U.S. Code § 1222(11)",
            href="https://www.law.cornell.edu/uscode/text/26/1222#11",
        ),
        dict(
            title="Maryland Comptroller Technical Bulletin No. 58, Maryland Taxation of Individual Capital Gain Income (Dec. 29, 2025), section I",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/technical-bulletins/tb-58.pdf#page=1",
        ),
        dict(
            title="2025 Maryland Form 502CG, line 1",
            href="https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/forms/2025/502cg.pdf#page=1",
        ),
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = ~person("is_tax_unit_dependent", period)
        # Capital gain distributions reported without Schedule D are
        # long-term capital gains (26 U.S.C. 852(b)(3)(B)). Form 1099-DIV box
        # 2a amounts are not negative, so each filer's input is floored at
        # zero, as in irs_gross_income. Distributions entered on Schedule D
        # line 13, and long-term loss carryovers, are already in
        # long_term_capital_gains.
        distributions = tax_unit.sum(
            filer * max_(0, person("non_sch_d_capital_gains", period))
        )
        # Schedule D line 15: net long-term capital gain or loss, 1222(7)-(8).
        long_term = (
            tax_unit_non_dep_add(tax_unit, period, ["long_term_capital_gains"])
            + distributions
        )
        # Schedule D line 16: line 15 plus the net short-term gain or loss.
        combined = long_term + tax_unit_non_dep_add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        # 1222(11): a net short-term capital loss reduces the net long-term
        # capital gain, and a net short-term capital gain does not add to it.
        # That is the smaller of Schedule D lines 15 and 16, as on line 7 of
        # the Schedule D Tax Worksheet. Form 502CG line 1 points to Form 502
        # line 1c, the Form 1040 line 7a gain, which would also count a net
        # short-term capital gain; the statute and Technical Bulletin 58 use
        # the 1222(11) amount.
        return max_(0, min_(long_term, combined))
