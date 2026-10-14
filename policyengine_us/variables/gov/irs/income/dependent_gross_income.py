from policyengine_us.model_api import *

# Gross income sources that dependent_gross_income and dependent_taxable_ss_magi
# replace. The model's taxable unemployment compensation and taxable Social
# Security allocate tax-unit amounts that depend on filing_status, which in
# turn depends on this variable through the qualifying relative test, so
# neither is read here.
DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES = {
    # Unemployment compensation is counted in full, reported or, when none is
    # reported, modeled state unemployment insurance. IRC 86(b)(2)(A) also
    # disregards the IRC 85(c) exclusion when figuring modified AGI.
    "taxable_unemployment_compensation": ["total_unemployment_compensation"],
    # Only the IRC 86 taxable part of Social Security is gross income. It is
    # computed in dependent_taxable_social_security, on the dependent's own
    # income, and modified AGI is figured without it (IRC 86(b)(2)(A)).
    "taxable_social_security": [],
    # Gross income includes gains but not losses (computed below). Modified
    # AGI nets them, subject to the IRC 1211(b) limit.
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
    the extent it is taxable under IRC 86 on the dependent's own return.
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
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        gross_income = 0
        for source in sources:
            components = DEPENDENT_GROSS_INCOME_SOURCE_OVERRIDES.get(source, [source])
            for component in components:
                # Add positive values only.
                gross_income += max_(0, add(person, period, [component]))

        if "capital_gains" in sources:
            # Long-term and short-term gains are each floored at zero instead
            # of being netted. The floored parts never sum to less than their
            # net, so taking the larger of the two changes nothing when
            # capital_gains is computed from its parts, and keeps a net
            # capital_gains value supplied directly as an input.
            long_term_gains = max_(0, person("long_term_capital_gains", period))
            short_term_gains = max_(0, person("short_term_capital_gains", period))
            net_capital_gains = person("capital_gains", period)
            gross_income += max_(long_term_gains + short_term_gains, net_capital_gains)

        if "taxable_social_security" in sources:
            gross_income += person("dependent_taxable_social_security", period)

        # Only dependents' own income is tested.
        is_dependent = ~person("is_tax_unit_head_or_spouse", period)
        return is_dependent * gross_income
