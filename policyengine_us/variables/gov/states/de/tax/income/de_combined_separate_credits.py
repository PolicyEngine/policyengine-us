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
    - which column takes the non-refundable EITC: 30 Del. C. 1117(b) and
      PIT-RSS Schedule II Line 12 select the spouse with greater tax remaining
      after other credits. Compare those balances within each allocation.
    The model permits either CDCC column on equal Line 23 incomes; this
    tie-election reading is retained by Max (d1684), rather than established
    explicitly in the instructions. Equal remaining taxes permit either EITC
    recipient.
    The dependent split and credit recipients are chosen together to minimise
    the two columns' tax after the EITC. Each column keeps its own $110 personal
    credit, if the filer cannot be claimed as a dependent elsewhere, and its
    aged credit.
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
    # The separate columns apply their own limits; pooled applied credits
    # have already been capped against the joint-return computation.
    cdcc = tax_unit("de_cdcc_potential", period)
    eitc = tax_unit("de_non_refundable_eitc_potential", period)
    head_own = where(tax_unit("head_is_dependent_elsewhere", period), 0, credit_per)
    spouse_own = where(tax_unit("spouse_is_dependent_elsewhere", period), 0, credit_per)
    own_units = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
    dep_units = max_(tax_unit("exemptions_count", period) - own_units, 0)

    # Max (d1684) retains the CDCC tie election (rulespec-us#1607) and selects
    # the statutory EITC rule: 1117(b) and PIT-RSS Schedule II line 12 compare
    # tax remaining before EITC, after each candidate's other credits.
    # https://delcode.delaware.gov/title30/c011/sc02/index.html#1114
    # https://delcode.delaware.gov/title30/c011/sc02/index.html#1117
    # https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10
    # https://revenuefiles.delaware.gov/2025/PITForms_Instructions/PIT-RSS_2025-01_PaperInteractiveIPM.pdf#page=1
    head_may_take_cdcc = head_taxable <= spouse_taxable
    spouse_may_take_cdcc = spouse_taxable <= head_taxable

    def line33(tax, own, aged, dependent_units, care_credit):
        # Match the stored float32 personal credit, then the float32 credit
        # addition and Line 33 subtraction in the downstream person formulas.
        # Scoring unrounded credits can select different final taxes after a
        # label swap. Aggregating each stored column promotes it to float64.
        personal = (own + dependent_units * credit_per).astype(np.float32)
        credits = personal + aged.astype(np.float32) + care_credit
        tax = tax.astype(np.float32)
        return (tax - min_(credits, tax)).astype(np.float64)

    # Keep the first choice only when the downstream tax is exactly equal.
    # Allocations may differ on ties, but their final liabilities must agree.
    best_tax = np.full_like(head_tax, np.inf)
    best_n = np.zeros_like(head_tax)
    best_cdcc_head = np.zeros_like(head_tax, dtype=bool)
    best_eitc_head = np.zeros_like(head_tax, dtype=bool)
    for n in range(int(dep_units.max(initial=0)) + 1):
        for cdcc_head in (False, True):
            for eitc_head in (True, False):
                head_line33 = line33(head_tax, head_own, head_aged, n, cdcc_head * cdcc)
                spouse_line33 = line33(
                    spouse_tax,
                    spouse_own,
                    spouse_aged,
                    dep_units - n,
                    (not cdcc_head) * cdcc,
                )
                allowed = (
                    (n <= dep_units)
                    & where(cdcc_head, head_may_take_cdcc, spouse_may_take_cdcc)
                    & where(
                        eitc_head,
                        head_line33 >= spouse_line33,
                        spouse_line33 >= head_line33,
                    )
                )
                head_eitc = min_(eitc, head_line33) if eitc_head else 0
                spouse_eitc = min_(eitc, spouse_line33) if not eitc_head else 0
                total = (
                    max_(head_line33 - head_eitc, 0)
                    + max_(spouse_line33 - spouse_eitc, 0)
                ).astype(np.float32)
                better = allowed & (total < best_tax)
                best_tax = where(better, total, best_tax)
                best_n = where(better, n, best_n)
                best_cdcc_head = where(better, cdcc_head, best_cdcc_head)
                best_eitc_head = where(better, eitc_head, best_eitc_head)
    return best_n, best_cdcc_head, best_eitc_head
