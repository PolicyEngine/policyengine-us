from policyengine_us.model_api import *


def ar_main_income_tax(taxable_income, p):
    """Arkansas regular income tax on net taxable income, before the $0 floor.

    `p` is `parameters(period).gov.states.ar.tax.income.rates.main`.

    Years with a published DFA Indexed Tax Brackets card apply the card:
    rate times taxable income, minus the card's reduction ("minus adjustment").

    Later years apply the statutory tables of A.C.A. 26-51-201(a)(4), whose
    bracket bounds 26-51-201(a)(5) and (d)(1) index each year, rounded to the
    nearest $100:
    - (A) net income at or below the high-income threshold: the rate table at
      marginal rates, each from its row's lower bound;
    - (B) net income above it: the high-income marginal rate table, applied to
      all of that income,
    - (C) less the fixed bracket adjustment for the row the income falls in.
    Taxing at marginal rates keeps tax continuous at every (A) and (B) row bound
    wherever indexing moves them; a stored reduction would not move with them.
    As in the statute, tax still steps where (A) meets (B)-(C) (down $2.66 at
    2026's $94,700) and rises by the $10 adjustment step at each (C) row bound.
    """
    if p.use_published_reduction:
        rate = p.rate.calc(taxable_income)
        return rate * taxable_income - p.reduction.calc(taxable_income)
    high_income = p.high_income
    table_a_tax = marginal_tax(p.rate, taxable_income)
    table_b_tax = high_income.rate.calc(taxable_income)
    # Thresholds are the "Less Than or Equal To" bound of the prior row.
    bracket_adjustment = high_income.bracket_adjustment.calc(taxable_income, right=True)
    return where(
        taxable_income <= high_income.threshold,
        table_a_tax,
        table_b_tax - bracket_adjustment,
    )


def marginal_tax(rate_scale, income):
    """Tax at the rates of a single_amount scale keyed by each row's lower bound,
    applied to the income within each row."""
    thresholds = rate_scale.thresholds
    rates = rate_scale.amounts
    tax = 0
    for i, (lower, rate) in enumerate(zip(thresholds, rates)):
        if lower == np.inf:
            break
        upper = thresholds[i + 1] if i + 1 < len(thresholds) else np.inf
        tax += rate * np.clip(income - lower, 0, upper - lower)
    return tax
