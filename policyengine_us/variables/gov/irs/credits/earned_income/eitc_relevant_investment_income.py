from policyengine_us.model_api import *


class eitc_relevant_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC-relevant investment income"
    documentation = (
        "Disqualified income of the head and spouse under 26 USC 32(i)(2), "
        "figured as on Publication 596 Worksheet 1. A tax unit dependent's "
        "interest, dividends, rents, passive income and capital gains are on "
        "the dependent's own return, as in irs_gross_income. The worksheet "
        "picks up a child's interest and dividends only through a Form 8814 "
        "election (lines 2 and 4), which is not modeled. A net_capital_gains "
        "amount supplied for the tax unit is read as covering every member, "
        "before any dependent's gains and losses are taken out."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/f8814--2025.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # Publication 596 Worksheet 1 keeps portfolio income, net capital
        # gains, and net passive income in separate baskets. A loss in one
        # basket cannot offset positive income in another.
        portfolio_income = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "taxable_interest_income",
                "tax_exempt_interest_income",
                "dividend_income",
            ],
        )
        # Worksheet 1 line 5: Form 1040 line 7a, the head and spouse's
        # Schedule D gain with capital gain distributions (line 13), or zero
        # if a loss. Start from net_capital_gains so a tax unit amount
        # supplied there is kept; it is read as covering every member, and
        # any dependent's gains and losses are then taken out. Capital gain
        # distributions (Form 1099-DIV box 2a) are not negative, so each
        # filer's input is floored at zero, as in irs_gross_income.
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        dependent_gains = tax_unit.sum(
            dependent
            * (
                person("long_term_capital_gains", period)
                + person("short_term_capital_gains", period)
            )
        )
        distributions = tax_unit.sum(
            ~dependent * max_(0, person("non_sch_d_capital_gains", period))
        )
        capital_gains = (
            tax_unit("net_capital_gains", period) - dependent_gains + distributions
        )
        # The model's undifferentiated rental input is treated as passive
        # rental income, consistently with its NIIT income mapping. Net the
        # passive amounts across the head and spouse before applying the zero
        # floor.
        passive_income = tax_unit_non_dep_add(
            tax_unit, period, ["rental_income", "passive_partnership_s_corp_income"]
        )
        return portfolio_income + max_(0, capital_gains) + max_(0, passive_income)
