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
        "is not read. The passive basket (lines 11-13) nets rental income, "
        "farm rental income, passive partnership and S corporation income "
        "and passive estate and trust income (Schedule E line 34a column (d) "
        "less line 34b column (c)), less "
        "eitc_passive_income_also_in_earned_income, then floors the result at "
        "zero. All rental and farm rental income is treated as passive: the "
        "model has no input for a real estate professional's nonpassive farm "
        "rental, whose loss Form 4835 says is not subject to the passive "
        "activity loss limitations. The estate and trust amount is "
        "passive_estate_income, the passive subset of estate_income, which "
        "defaults to zero; nonpassive estate and trust income (Schedule E "
        "Part III columns (e) and (f), such as Schedule K-1 (Form 1041) box 5 "
        "annuities and income in respect of a decedent) is not on lines 11 "
        "and 12."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/f8814--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i8814--2025.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/f4835--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/f1040se--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i1041sk1--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-pdf/p4801.pdf#page=50",
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
        # Worksheet 1 lines 11-13. The model's undifferentiated rental input is
        # treated as passive rental income, consistently with its NIIT income
        # mapping. Farm rental income (Form 4835, Schedule E line 40, which
        # lines 11 and 12 name) is treated as passive in the same way; Form
        # 4835 is for rental activities under the passive activity rules,
        # and the model has no input for a real estate professional's
        # nonpassive farm rental. Lines 11 and 12 also name Schedule E line
        # 34a column (d) and line 34b column (c), the passive income and loss
        # from estates and trusts (Schedule K-1 (Form 1041) boxes 6 through 8
        # when passive to the beneficiary), not the nonpassive columns (e) and
        # (f), which carry box 5 annuities and income in respect of a decedent.
        # estate_income is the Part III total, so the passive part is the
        # separate passive_estate_income input. It defaults to zero, like
        # passive_partnership_s_corp_income, rather than to all of
        # estate_income as rental income is treated: most Part III income is
        # nonpassive (38% of positive Part III income was passive in tax year
        # 2023, SOI Publication 4801). 32(i)(2)(E) determines passive income
        # and losses without regard to amounts included in earned income, so
        # the signed part of passive income also in earned income is removed.
        # Net the passive amounts across the head and spouse before applying
        # the zero floor, so a passive estate or trust loss offsets other
        # passive income but never interest, dividends or capital gains.
        passive_income = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "rental_income",
                "farm_rent_income",
                "passive_partnership_s_corp_income",
                "passive_estate_income",
            ],
        ) - tax_unit_non_dep_add(
            tax_unit, period, ["eitc_passive_income_also_in_earned_income"]
        )
        return portfolio_income + max_(0, capital_gains) + max_(0, passive_income)
