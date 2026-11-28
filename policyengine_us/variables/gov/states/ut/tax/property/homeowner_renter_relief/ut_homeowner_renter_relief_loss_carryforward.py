from policyengine_us.model_api import *


def carryover_claimed(net_gain, carryover, loss_limit):
    """The part of a capital loss carryover a return uses in the year.

    A return's capital gain or loss in adjusted gross income is its net gain,
    or its net loss up to the IRC 1211(b) limit. `net_gain` already includes
    the carryover as a loss, so the carryover claimed is that amount without
    the carryover less the amount with it. The rest is carried on.
    """
    return max_(net_gain + carryover, -loss_limit) - max_(net_gain, -loss_limit)


class ut_homeowner_renter_relief_loss_carryforward(Variable):
    value_type = float
    entity = Person
    label = "Utah homeowner's/renter's relief loss carryforwards claimed"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The capital loss carryforward claimed in the year: how much the "
        "long-term capital loss carried from earlier years "
        "(long_term_capital_loss_carryover) lowered federal adjusted gross "
        "income. Utah counts loss carryforwards claimed during the year as "
        "nontaxable income (Utah Code 59-2a-101(20)(a)(ii)), and Form TC-90CB "
        "line 5 reports capital gain or loss without carryforwards. The "
        "carryover offsets the year's capital gains and can add to a net "
        "capital loss up to the IRC 1211(b) limit; the unused rest is carried "
        "on and adds nothing. The amount for the head and spouse's return is "
        "on the head; a tax unit dependent's own return is figured "
        "separately. No short-term carryover or net operating loss "
        "carryforward is modeled, so neither is added back."
    )
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=4",
        "https://files.tax.utah.gov/tax/forms/current/tc-90cb.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
    )
    defined_for = StateCode.UT

    def formula(person, period, parameters):
        p = parameters(period).gov.irs
        sources = p.gross_income.sources
        carryover = max_(0, person("long_term_capital_loss_carryover", period))
        # No carryover reaches adjusted gross income when a reform takes
        # capital gains out of gross income.
        if "capital_gains" not in sources:
            return 0 * carryover
        # long_term_capital_gains already includes the carryover as a loss, as
        # Schedule D line 15 does. Capital gain distributions net with the
        # year's gains and losses on Schedule D line 13.
        net_gain = person("capital_gains", period)
        if "non_sch_d_capital_gains" in sources:
            net_gain = net_gain + max_(0, person("non_sch_d_capital_gains", period))
        # Without the loss deduction a net loss lowers no adjusted gross
        # income.
        deduct_losses = "loss_ald" in p.ald.deductions
        loss_limit = p.ald.loss.capital.max
        is_dependent = person("is_tax_unit_dependent", period)
        # The head and spouse's return combines their gains, losses and
        # carryovers under one limit, as limited_capital_loss does.
        tax_unit = person.tax_unit
        filer = ~is_dependent
        filing_status = tax_unit("filing_status", period)
        return_claimed = carryover_claimed(
            tax_unit.sum(filer * net_gain),
            tax_unit.sum(filer * carryover),
            deduct_losses * loss_limit[filing_status],
        )
        head = person("is_tax_unit_head", period)
        # A dependent's own return, as dependent_adjusted_gross_income
        # figures it: a dependent who lives with their spouse files
        # separately; any other files as single.
        dependent_loss_limit = deduct_losses * where(
            person("dependent_lives_with_spouse", period),
            loss_limit["SEPARATE"],
            loss_limit["SINGLE"],
        )
        dependent_claimed = carryover_claimed(net_gain, carryover, dependent_loss_limit)
        return where(is_dependent, dependent_claimed, head * return_claimed)
