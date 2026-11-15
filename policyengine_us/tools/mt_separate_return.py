"""Montana separate filing on the same form (status 2a), column by column.

The functions below are the formulas of the status 2a column variables, taking
the amount a step depends on as an argument. The variables call them, and so
do the tax unit's choices that must compare the couple's tax under different
deductions without simulation branches: the split of a dependent's medical
bills (mt_dependent_medical_expense_head_share) and the itemize election
(mt_tax_unit_itemizes). Because both paths run the same code, the tax a choice
compares is the tax the columns then compute.
"""

import numpy as np

from policyengine_core.model_api import max_, min_, select, where


def mt_medical_deduction(person, period, parameters, line_1a):
    """Each column's medical deduction given its line 1a amount.

    While the Itemized Deductions Schedule applies (2021-2023), line 1 floors
    the medical and dental expenses other than premiums (line 1a) at 7.5% of
    the column's Montana AGI, and lines 2 and 3 add the medical and long-term
    care insurance premiums in full. In a later year (a reform allowing
    separate filing) the premiums stay under the floor with the other
    expenses. Zero for members other than the head and spouse.
    """
    p = parameters(period).gov.states.mt.tax.income.deductions.itemized
    floor = parameters(period).gov.irs.deductions.itemized.medical.floor
    medical_floor = floor * person("mt_agi_indiv", period)
    premiums = person("mt_eligible_medical_insurance_premiums", period)
    if p.state_specific_deduction_applies:
        long_term_care_premiums = person(
            "mt_eligible_long_term_care_insurance_premiums", period
        )
        deduction = (
            max_(0, line_1a - medical_floor) + premiums + long_term_care_premiums
        )
    else:
        deduction = max_(0, premiums + line_1a - medical_floor)
    return person("is_tax_unit_head_or_spouse", period) * deduction


def mt_medical_floor_room(person, period, parameters):
    """How much more line 1a each column can take before its floor binds.

    The 7.5% floor less what is already under it in the column: the column's
    own other medical expenses, and from 2024 its premiums too. Negative when
    the column is already above its floor.
    """
    p = parameters(period).gov.states.mt.tax.income.deductions.itemized
    floor = parameters(period).gov.irs.deductions.itemized.medical.floor
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    under_floor = head_or_spouse * person("other_medical_expenses", period)
    if not p.state_specific_deduction_applies:
        under_floor = under_floor + person(
            "mt_eligible_medical_insurance_premiums", period
        )
    return floor * person("mt_agi_indiv", period) - under_floor


def mt_allocate_dependent_exemptions(person, period, pre_dependent_exemption_income):
    """Taxable income in each column after the dependent exemptions.

    The dependent exemptions are allocated optimally between the head and
    spouse: first to the column with the larger income, up to the difference
    between the two, and the rest halved.
    """
    dependent_exemptions = person.tax_unit.sum(
        person("mt_dependent_exemptions_person", period)
    )
    head = person("is_tax_unit_head", period)
    spouse = person("is_tax_unit_spouse", period)
    head_income = person.tax_unit.sum(pre_dependent_exemption_income * head)
    spouse_income = person.tax_unit.sum(pre_dependent_exemption_income * spouse)
    # Cap the exemption amount initially at the difference between the head
    # and spouse income, and allocate it to the spouse with the larger income.
    income_difference = np.abs(head_income - spouse_income)
    capped = min_(income_difference, dependent_exemptions)
    larger = where(head_income > spouse_income, head, spouse)
    # The remaining exemption amount is halved between the head and spouse.
    halved_remaining = (dependent_exemptions - capped) / 2
    return max_(pre_dependent_exemption_income - capped * larger - halved_remaining, 0)


def _filing_status(person, period):
    filing_status = person.tax_unit(
        "state_filing_status_if_married_filing_separately_on_same_return", period
    )
    return filing_status, filing_status.possible_values


def _net_long_term_capital_gain(person, period):
    # Montana Form 2 line 2 uses the federal net long-term capital gain
    # amount, which is limited by any short-term capital losses.
    ltcg = person("long_term_capital_gains", period)
    stcg = person("short_term_capital_gains", period)
    return max_(min_(ltcg, ltcg + stcg), 0)


def mt_regular_tax(person, period, parameters, taxable_income):
    """Each column's tax on taxable income from the rate schedule."""
    p = parameters(period).gov.states.mt.tax.income.main
    if p.capital_gains.in_effect:
        taxable_income = max_(
            taxable_income - _net_long_term_capital_gain(person, period), 0
        )
    filing_status, status = _filing_status(person, period)
    return select(
        [
            filing_status == status.SINGLE,
            filing_status == status.HEAD_OF_HOUSEHOLD,
            filing_status == status.SEPARATE,
            filing_status == status.SURVIVING_SPOUSE,
        ],
        [
            p.single.calc(taxable_income),
            p.head_of_household.calc(taxable_income),
            p.separate.calc(taxable_income),
            p.surviving_spouse.calc(taxable_income),
        ],
    )


def mt_capital_gains_threshold(person, period, parameters, taxable_income):
    """The part of the lower capital gains rate band left after ordinary income."""
    p = parameters(period).gov.states.mt.tax.income.main.capital_gains
    capital_gains = _net_long_term_capital_gain(person, period)
    filing_status, status = _filing_status(person, period)
    non_qualified_income = max_(taxable_income - capital_gains, 0)
    rate_threshold = select(
        [
            filing_status == status.SINGLE,
            filing_status == status.SEPARATE,
            filing_status == status.HEAD_OF_HOUSEHOLD,
            filing_status == status.SURVIVING_SPOUSE,
        ],
        [
            p.rates.single.thresholds[-1],
            p.rates.separate.thresholds[-1],
            p.rates.head_of_household.thresholds[-1],
            p.rates.surviving_spouse.thresholds[-1],
        ],
    )
    return max_(rate_threshold - non_qualified_income, 0)


def mt_capital_gains_tax(person, period, parameters, applicable_threshold):
    """Each column's tax on net long-term capital gains (from 2024)."""
    p = parameters(period).gov.states.mt.tax.income.main.capital_gains
    if not p.in_effect:
        return 0
    capital_gains = _net_long_term_capital_gain(person, period)
    filing_status, status = _filing_status(person, period)
    statuses = [
        filing_status == status.SINGLE,
        filing_status == status.SEPARATE,
        filing_status == status.SURVIVING_SPOUSE,
        filing_status == status.HEAD_OF_HOUSEHOLD,
    ]
    schedules = [
        p.rates.single,
        p.rates.separate,
        p.rates.surviving_spouse,
        p.rates.head_of_household,
    ]
    lower_rate = select(statuses, [s.amounts[0] for s in schedules])
    higher_rate = select(statuses, [s.amounts[-1] for s in schedules])
    below = min_(applicable_threshold, capital_gains)
    above = max_(capital_gains - applicable_threshold, 0)
    return max_(below * lower_rate + above * higher_rate, 0)


def mt_separate_tax_before_refundable_credits(tax_unit, period, parameters, deductions):
    """The couple's combined status 2a tax before refundable credits.

    deductions is each person's deduction (the head's and spouse's columns;
    zero for other members). This follows the column variables from
    mt_pre_dependent_exemption_taxable_income_indiv to
    mt_income_tax_before_refundable_credits_indiv (Form 2 line 20 in each
    column) and sums the columns. Refundable credits do not depend on the
    deductions, except the 2021 income tax rebate, which is capped at line
    20 and so is left out of the comparison.
    """
    person = tax_unit.members
    agi = person("mt_agi_indiv", period)
    exemptions = person("mt_personal_exemptions_indiv", period)
    pre_dependent_exemption_income = max_(agi - exemptions - deductions, 0)
    taxable_income = mt_allocate_dependent_exemptions(
        person, period, pre_dependent_exemption_income
    )
    regular_tax = mt_regular_tax(person, period, parameters, taxable_income)
    threshold = mt_capital_gains_threshold(person, period, parameters, taxable_income)
    capital_gains_tax = mt_capital_gains_tax(person, period, parameters, threshold)
    non_refundable_credits = person("mt_non_refundable_credits", period)
    head_or_spouse = person("is_tax_unit_head_or_spouse", period)
    line_20 = head_or_spouse * max_(
        regular_tax + capital_gains_tax - non_refundable_credits, 0
    )
    return tax_unit.sum(line_20)
