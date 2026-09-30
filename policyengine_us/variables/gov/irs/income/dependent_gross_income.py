from policyengine_us.model_api import *

# Gross income sources that dependent_gross_income replaces. The model's
# taxable unemployment compensation and taxable Social Security allocate
# tax-unit amounts that depend on filing_status, which in turn depends on this
# variable through the qualifying relative test, so neither is read here.
DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES = {
    # Unemployment compensation is counted in full.
    "taxable_unemployment_compensation": ["unemployment_compensation"],
    # Only the IRC 86 taxable part of Social Security is gross income. It is
    # computed below on the dependent's own income.
    "taxable_social_security": [],
    # Gross income includes gains but not losses. Computed below.
    "capital_gains": [],
}


class dependent_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income for dependents"
    unit = USD
    documentation = """
    Gross income for dependents, used for the qualifying relative income test
    under IRC 152(d)(1)(B). Mirrors irs_gross_income but calculates income for
    dependents (not head or spouse) instead of non-dependents. Capital gains
    are counted without netting losses, and Social Security counts only to
    the extent it is taxable under IRC 86 on the dependent's own income.
    """
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.law.cornell.edu/uscode/text/26/152#d_1_B",
        # Treas. Reg. 1.61-6(a): gain realized on the sale or exchange of
        # property is included in gross income.
        "https://www.law.cornell.edu/cfr/text/26/1.61-6",
        # IRS Pub. 501 (2022): gross income "includes gains, but not losses",
        # and Social Security counts only when taxable.
        "https://www.irs.gov/pub/irs-prior/p501--2022.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p501--2022.pdf#page=19",
        # IRS Pub. 915 (2022): a dependent's benefits are added to the
        # dependent's own other income to determine their taxable part.
        "https://www.irs.gov/pub/irs-prior/p915--2022.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs
        sources = p.gross_income.sources
        other_gross_income = 0
        for source in sources:
            components = DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES.get(source, [source])
            for component in components:
                # Add positive values only.
                other_gross_income += max_(0, add(person, period, [component]))

        if "capital_gains" in sources:
            # Long-term and short-term gains are each floored at zero instead
            # of being netted. The floored parts never sum to less than their
            # net, so taking the larger of the two changes nothing when
            # capital_gains is computed from its parts, and keeps a net
            # capital_gains value supplied directly as an input.
            long_term_gains = max_(0, person("long_term_capital_gains", period))
            short_term_gains = max_(0, person("short_term_capital_gains", period))
            net_capital_gains = person("capital_gains", period)
            other_gross_income += max_(
                long_term_gains + short_term_gains, net_capital_gains
            )

        # Taxable Social Security under IRC 86, computed on the dependent's
        # own income with the single base amounts, so that it does not depend
        # on filing_status. Pub. 501: benefits are not gross income unless
        # "one-half of your social security benefits plus your other gross
        # income and any tax-exempt interest" exceeds the base amount.
        # Approximations: adjustments to income are ignored, and the $0 base
        # for a dependent who is married filing separately and lives with
        # their spouse is not modeled.
        ss = p.social_security.taxability
        social_security = max_(0, person("social_security", period))
        provisional_income = (
            other_gross_income
            + person("tax_exempt_interest_income", period)
            + ss.combined_income_ss_fraction * social_security
        )
        base_amount = ss.threshold.base.main["SINGLE"]
        adjusted_base_amount = ss.threshold.adjusted_base.main["SINGLE"]
        # IRC 86(a)(1): the lesser of half the benefits or half the excess of
        # provisional income over the base amount.
        amount_under_paragraph_1 = min_(
            ss.rate.base.benefit_cap * social_security,
            ss.rate.base.excess * max_(0, provisional_income - base_amount),
        )
        # IRC 86(a)(2): above the adjusted base amount.
        bracket_amount = min_(
            amount_under_paragraph_1,
            ss.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )
        amount_over_adjusted_base = min_(
            ss.rate.additional.excess
            * max_(0, provisional_income - adjusted_base_amount)
            + bracket_amount,
            ss.rate.additional.benefit_cap * social_security,
        )
        taxable_social_security = select(
            [
                provisional_income < base_amount,
                provisional_income < adjusted_base_amount,
            ],
            [0, amount_under_paragraph_1],
            default=amount_over_adjusted_base,
        )
        counts_social_security = "taxable_social_security" in sources
        gross_income = (
            other_gross_income + counts_social_security * taxable_social_security
        )
        # Only dependents' own income is tested.
        is_dependent = ~person("is_tax_unit_head_or_spouse", period)
        return is_dependent * gross_income
