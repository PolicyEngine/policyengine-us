from policyengine_us.model_api import *


class me_fairness_credit_netted_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine fairness credit capital losses netted against a filer's own gains"
    unit = USD
    documentation = (
        "The capital losses of the head and spouse that offset the same "
        "person's gains inside capital_gains, which 36 M.R.S. 5213-A(1)(B)(1) "
        "and 5219-KK(1)(D)(1) add back to federal adjusted gross income for "
        "the fairness credits: a short-term or long-term loss that offset the "
        "gain in the other holding period or capital gain distributions on "
        "Schedule D line 13, and the prior-year long-term capital loss "
        "carryover to the extent the same person's gains absorbed it. "
        "irs_gross_income leaves out each filer's net capital loss, so the "
        "fairness credit income already adds back the capital losses "
        "adjusted gross income deducts from it."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B. (1)
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D. (1)
        "https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
        "https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=1",  # lines 7, 13-15
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # capital_gains nets each person's short-term and long-term gains
        # (Schedule D lines 7 and 15) before irs_gross_income floors the
        # total at zero, so a loss that offsets the same person's gain in the
        # other part reduces irs_gross_income itself, unlike the losses it
        # leaves out. Long-term gains also net two items Schedule D lists on
        # their own lines: capital gain distributions (line 13) and the
        # prior-year long-term capital loss carryover (line 14), which
        # 26 U.S.C. 1212(b)(1)(B) treats as a long-term capital loss of the
        # year.
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
        netted = min_(gains, losses)
        # A tax unit dependent's items are on the dependent's own return, as
        # in irs_gross_income.
        not_dependent = ~person("is_tax_unit_dependent", period)
        # No capital loss is in adjusted gross income when a reform takes
        # capital gains out of gross income.
        sources = parameters(period).gov.irs.gross_income.sources
        capital_gains_counted = "capital_gains" in sources
        return capital_gains_counted * tax_unit.sum(not_dependent * netted)
