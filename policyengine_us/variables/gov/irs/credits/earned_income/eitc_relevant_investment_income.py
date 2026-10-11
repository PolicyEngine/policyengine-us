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
        "picks up a child's income only through a Form 8814 election: line 2 "
        "adds Form 8814 line 1b, line 4 the Schedule 1 line 8z amount, and the "
        "elected dividends and capital gain distributions reach lines 3 and 5 "
        "through Form 1040 lines 3b and 7a. The election is not modeled, which "
        "can overstate the credit for a parent who makes it. Capital gains "
        "are the head's and spouse's own long_term_capital_gains and "
        "short_term_capital_gains; a net_capital_gains amount supplied for "
        "the tax unit, or a capital_gains amount set directly on a person, "
        "is not read."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/f8814--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i8814--2025.pdf#page=4",
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
        # if a loss. Sum their own gains and losses directly, as the NIIT base
        # (filer_loss_limited_net_capital_gains) does. Reading the tax unit's
        # net_capital_gains and taking dependents' gains out of it would let a
        # dependent's large gain move the filers' amount through float32
        # rounding of the total, and core does not record which tax units
        # supplied that total. So a net_capital_gains amount supplied for the
        # tax unit is not read.
        filer_gains = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains", "short_term_capital_gains"]
        )
        # Capital gain distributions (Form 1099-DIV box 2a) are not negative,
        # so each filer's input is floored at zero, as in irs_gross_income.
        person = tax_unit.members
        distributions = tax_unit.sum(
            ~person("is_tax_unit_dependent", period)
            * max_(0, person("non_sch_d_capital_gains", period))
        )
        capital_gains = filer_gains + distributions
        # The model's undifferentiated rental input is treated as passive
        # rental income, consistently with its NIIT income mapping. Net the
        # passive amounts across the head and spouse before applying the zero
        # floor.
        passive_income = tax_unit_non_dep_add(
            tax_unit, period, ["rental_income", "passive_partnership_s_corp_income"]
        )
        return portfolio_income + max_(0, capital_gains) + max_(0, passive_income)
