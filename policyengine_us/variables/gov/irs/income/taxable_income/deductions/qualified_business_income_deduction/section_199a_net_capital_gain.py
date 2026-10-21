from policyengine_us.model_api import *


class section_199a_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain for the qualified business income deduction"
    unit = USD
    documentation = (
        "Net capital gain under 26 U.S.C. 1222(11) plus qualified dividend "
        "income, the amount subtracted from taxable income in the 26 U.S.C. "
        "199A(a)(2) income limitation (Form 8995 line 12, Form 8995-A line "
        "34). Unlike adjusted net capital gain, it keeps unrecaptured section "
        "1250 gain and 28-percent rate gain. Unlike net_capital_gain, it is "
        "not reduced by a Form 4952 investment income election. It counts the "
        "head's and spouse's gains and dividends only: a tax unit dependent's "
        "are on the dependent's own return, as taxable income already leaves "
        "them off this one."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 199A(a)(2)(B)",
            href="https://www.law.cornell.edu/uscode/text/26/199A#a_2_B",
        ),
        dict(
            title="26 CFR § 1.199A-1(b)(3)",
            href="https://www.ecfr.gov/current/title-26/part-1/section-1.199A-1#p-1.199A-1(b)(3)",
        ),
        dict(
            title="26 U.S. Code § 1222(11)",
            href="https://www.law.cornell.edu/uscode/text/26/1222#11",
        ),
        dict(
            title="2025 Instructions for Form 8995, line 12",
            href="https://www.irs.gov/pub/irs-prior/i8995--2025.pdf#page=4",
        ),
        dict(
            title="2025 Instructions for Form 8995-A, line 34",
            href="https://www.irs.gov/pub/irs-prior/i8995a--2025.pdf#page=7",
        ),
        dict(
            title="TD 9847, Net Capital Gain, 84 FR 2954",
            href="https://www.govinfo.gov/content/pkg/FR-2019-02-08/pdf/2019-01025.pdf#page=3",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Treas. Reg. 1.199A-1(b)(3): "net capital gain as defined in section
        # 1222(11) plus any qualified dividend income (as defined in section
        # 1(h)(11)(B))". Neither part is reduced by a Form 4952 line 4g
        # election: the form uses Form 1040 line 3a, which the Form 4952
        # instructions say not to reduce, and Schedule D lines 15 and 16.
        # TD 9847's preamble explicitly confirms that elected gains and
        # dividends remain net capital gain for the section 199A deduction.
        # Schedule D line 15: net long-term gain, including capital gain
        # distributions (long-term under 26 U.S.C. 852(b)(3)(B)). Without
        # Schedule D, net capital gain is Form 1040 line 7a.
        # Dependents' amounts are left out before netting, so a dependent's
        # loss never offsets the filer's gain.
        long_term_gain = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        # Schedule D line 16: line 7 (net short-term gain) plus line 15.
        combined_gain = long_term_gain + tax_unit_non_dep_add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        # "The smaller of Schedule D (Form 1040), line 15 or 16, unless line
        # 15 or 16 is zero or less, in which case nothing is added to the
        # qualified dividends."
        net_capital_gain = max_(0, min_(long_term_gain, combined_gain))
        qualified_dividends = max_(
            0, tax_unit_non_dep_add(tax_unit, period, ["qualified_dividend_income"])
        )
        return net_capital_gain + qualified_dividends
