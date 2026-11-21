from policyengine_us.model_api import *


class vt_renter_credit_capital_loss_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit capital loss add-back"
    unit = USD
    documentation = (
        "The capital losses that 32 V.S.A. 6061(18)(A) adds back to federal "
        "adjusted gross income for the renter credit: each capital loss of "
        "the head and spouse that adjusted gross income deducted, whether "
        "the same person's gains, another filer's gains or capital gain "
        "distributions absorbed it, or it is part of the net capital loss up "
        "to the 26 U.S.C. 1211(b) limit. A loss carried to a later year is "
        "not added back."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06061",  # (18)(A)
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
        "https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=1",  # lines 7, 13-15
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # Losses absorbed by gains outside each person's capital_gains
        # (another filer's gains, or capital gain distributions reported
        # without Schedule D), and the net capital loss up to the limit.
        deducted_outside_capital_gains = add(
            tax_unit,
            period,
            ["capital_losses_allowed_against_gains", "limited_capital_loss"],
        )
        # As in those two, no capital loss is deducted when a reform takes
        # capital gains out of gross income.
        if "capital_gains" not in parameters(period).gov.irs.gross_income.sources:
            return deducted_outside_capital_gains
        person = tax_unit.members
        # capital_gains nets each person's short-term and long-term gains
        # (Schedule D lines 7 and 15), so a loss in one part that offsets the
        # same person's gain in the other never reaches the deduction above.
        # Long-term gains also net two items Schedule D lists on their own
        # lines: capital gain distributions (line 13) and the prior-year
        # long-term capital loss carryover (line 14), which 26 U.S.C.
        # 1212(b)(1)(B) treats as a long-term capital loss of the year.
        short_term = person("short_term_capital_gains", period)
        long_term = person("long_term_capital_gains", period)
        # Without the parts, capital_gains is a net amount supplied directly;
        # it is taken as the long-term total the two items net into.
        parts_supplied = (short_term != 0) | (long_term != 0)
        long_term = where(parts_supplied, long_term, person("capital_gains", period))
        distributions = max_(0, person("schedule_d_capital_gain_distributions", period))
        carryover = max_(0, person("long_term_capital_loss_carryover", period))
        # The long-term gain or loss from sales and exchanges (lines 8 to 12).
        long_term_sales = long_term - distributions + carryover
        gains = max_(0, short_term) + max_(0, long_term_sales) + distributions
        losses = max_(0, -short_term) + max_(0, -long_term_sales) + carryover
        absorbed_within_person = min_(gains, losses)
        # A tax-unit dependent's capital gains and losses belong on the
        # dependent's own return, as in irs_gross_income.
        not_dependent = ~person("is_tax_unit_dependent", period)
        return deducted_outside_capital_gains + tax_unit.sum(
            not_dependent * absorbed_within_person
        )
