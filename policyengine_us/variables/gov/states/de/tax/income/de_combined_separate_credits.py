from policyengine_us.model_api import *


def de_combined_separate_credit_choices(tax_unit, period, parameters):
    """The taxpayer's choices for column credits on a combined separate return.

    On a Delaware combined separate return (Filing Status 4) the couple
    decides three things that move credits between the two columns:
    - how to split the dependents' $110 personal credits (PIT-RES Line 27a:
      "split the total between Columns A and B in increments of $110");
    - which column takes the dependent care credit, which "may only be
      applied against the tax imposed on the spouse with the lower taxable
      income reported on Line 23" (Line 31);
    - which column takes the non-refundable EITC, which "may only be applied
      against the tax imposed on the spouse with the higher taxable income
      reported on Line 23" (Line 34).
    With equal Line 23 incomes either column qualifies for Line 31 and Line 34.
    The dependent split, and the Line 31 and Line 34 columns where both
    qualify, are chosen together to minimise the two columns' tax after the
    EITC. Each column keeps its own $110 personal credit and aged credit.
    The search treats the spouses alike, so the minimum does not depend on
    which spouse is labelled head.

    Returns tax-unit arrays: the number of dependent increments in the head's
    column, whether the head's column takes the dependent care credit, and
    whether the head's column takes the EITC.
    """
    person = tax_unit.members
    is_head = person("is_tax_unit_head", period)
    is_spouse = person("is_tax_unit_spouse", period)

    def column(values):
        return tax_unit.sum(is_head * values), tax_unit.sum(is_spouse * values)

    p = parameters(period).gov.states.de.tax.income.credits
    credit_per = p.personal_credits.personal
    head_tax, spouse_tax = column(
        person("de_income_tax_before_non_refundable_credits_indv", period)
    )
    head_aged, spouse_aged = column(person("de_aged_personal_credit_indv", period))
    head_taxable, spouse_taxable = column(person("de_taxable_income_indv", period))
    cdcc = tax_unit("de_cdcc", period)
    eitc = tax_unit("de_non_refundable_eitc", period)
    dep_units = max_(tax_unit("exemptions_count", period) - 2, 0)

    # Columns allowed for each credit; both on equal Line 23 incomes.
    head_may_take_cdcc = head_taxable <= spouse_taxable
    spouse_may_take_cdcc = spouse_taxable <= head_taxable
    head_may_take_eitc = head_taxable >= spouse_taxable
    spouse_may_take_eitc = spouse_taxable >= head_taxable

    # Among choices with equal tax the first found is kept. The search tries
    # main's earlier tie routing first (dependent care credit to the spouse,
    # EITC to the head). That only matters when the columns are identical.
    best_tax = np.full_like(head_tax, np.inf)
    best_n = np.zeros_like(head_tax)
    best_cdcc_head = np.zeros_like(head_tax, dtype=bool)
    best_eitc_head = np.zeros_like(head_tax, dtype=bool)
    for n in range(int(dep_units.max(initial=0)) + 1):
        for cdcc_head in (False, True):
            for eitc_head in (True, False):
                allowed = (
                    (n <= dep_units)
                    & where(cdcc_head, head_may_take_cdcc, spouse_may_take_cdcc)
                    & where(eitc_head, head_may_take_eitc, spouse_may_take_eitc)
                )
                head_credits = (
                    credit_per + head_aged + n * credit_per + cdcc_head * cdcc
                )
                spouse_credits = (
                    credit_per
                    + spouse_aged
                    + (dep_units - n) * credit_per
                    + (not cdcc_head) * cdcc
                )
                # Line 33: each column's tax after its credits, at least zero.
                head_line33 = max_(head_tax - head_credits, 0)
                spouse_line33 = max_(spouse_tax - spouse_credits, 0)
                eitc_column = head_line33 if eitc_head else spouse_line33
                total = head_line33 + spouse_line33 - min_(eitc, eitc_column)
                better = allowed & (total < best_tax - 1e-6)
                best_tax = where(better, total, best_tax)
                best_n = where(better, n, best_n)
                best_cdcc_head = where(better, cdcc_head, best_cdcc_head)
                best_eitc_head = where(better, eitc_head, best_eitc_head)
    return best_n, best_cdcc_head, best_eitc_head
