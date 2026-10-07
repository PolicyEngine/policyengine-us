from policyengine_us.model_api import *


class mt_investment_interest_expense_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana investment interest deduction for separate returns"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = [
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=38",
        "https://www.irs.gov/pub/irs-prior/f4952--2023.pdf",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
    ]
    documentation = """
    Before 2024, Montana's Form 2 line 10 requires spouses filing separately
    to compute Form 4952 separately. Each spouse's current interest is
    limited to that spouse's net investment income, with the same modeled
    property classification, gain netting, and capped election as the federal
    form. Dependents' amounts do not enter either spouse's computation.

    Montana investment-income adjustments and separate-return carryovers
    are not modeled. The federal prior-year carryover input is at tax-unit
    level and cannot identify the carryover belonging to each spouse.
    Investment expenses follow the modeled federal miscellaneous deduction
    rules, applying any allowed expense pool and AGI floor separately.

    From 2024, Montana uses federal itemized deductions. This variable
    preserves the allocation of the federal deduction by filer interest
    shares. When no current interest was paid, the head carries any allowed
    federal carryover, matching the joint-return reporting convention.
    Montana no longer permits separate filing on the same return.
    """

    def formula(person, period, parameters):
        filer = person("is_tax_unit_head_or_spouse", period)
        interest = max_(0, person("investment_interest_expense", period))
        qualified_dividends = person("qualified_dividend_income", period)
        distributions = max_(0, person("non_sch_d_capital_gains", period))
        long_term_gains = person("long_term_capital_gains", period) + distributions
        short_term_gains = person("short_term_capital_gains", period)
        net_gain = max_(0, long_term_gains + short_term_gains)
        net_capital_gain = min_(
            net_gain, max_(0, long_term_gains - max_(0, -short_term_gains))
        )
        election = min_(
            max_(0, person("investment_income_elected_form_4952", period)),
            qualified_dividends + net_capital_gain,
        )
        gross_income = add(
            person, period, ["taxable_interest_income", "ordinary_dividend_income"]
        )
        investment_income = (
            gross_income - qualified_dividends + net_gain - net_capital_gain + election
        )
        p = parameters(period).gov.irs.deductions.itemized.misc
        if p.applies:
            misc_expenses = add(person, period, p.sources)
            own_agi = max_(0, person("adjusted_gross_income_person", period))
            allowed_misc = max_(0, misc_expenses - p.floor * own_agi)
            expenses = min_(person("investment_expenses", period), allowed_misc)
        else:
            expenses = 0
        net_investment_income = max_(0, investment_income - expenses)
        return filer * min_(interest, net_investment_income)

    def formula_2024(person, period, parameters):
        filer = person("is_tax_unit_head_or_spouse", period)
        interest = filer * max_(0, person("investment_interest_expense", period))
        total_interest = person.tax_unit.sum(interest)
        interest_share = np.divide(
            interest,
            total_interest,
            out=np.zeros_like(interest),
            where=total_interest > 0,
        )
        # Preserve a carryover-only federal deduction using the existing
        # joint-return reporting convention, without assigning ownership.
        interest_share = where(
            total_interest > 0,
            interest_share,
            person("is_tax_unit_head", period),
        )
        return (
            person.tax_unit("investment_interest_expense_deduction", period)
            * interest_share
        )
