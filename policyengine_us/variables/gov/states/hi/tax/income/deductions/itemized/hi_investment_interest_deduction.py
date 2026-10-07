from policyengine_us.model_api import *


class hi_investment_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii investment interest deduction"
    unit = USD
    documentation = (
        "Form N-158 line 8. IRC 163(d) limits investment interest to net "
        "investment income. Hawaii makes IRC 163(d)(4)(B) inoperative, so "
        "qualified dividends count as investment income without an election."
    )
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0002_0004.htm",
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0007.htm",
        "https://files.hawaii.gov/tax/forms/2025/n158_i.pdf",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # Line 3. The line 2 carryforward from the prior year is not modeled.
        interest_expense = tax_unit_non_dep_add(
            tax_unit, period, ["investment_interest_expense"]
        )
        # Line 4a excludes dependents unless an N-814 election is filed.
        # That election is not modeled. Federal-obligation interest is exempt
        # under HRS 235-7(a)(1), so it is not Hawaii investment income.
        taxable_interest = tax_unit_non_dep_add(
            tax_unit, period, ["taxable_interest_income"]
        )
        dependent_government_interest = tax_unit.sum(
            tax_unit.members("us_govt_interest_person", period)
            * tax_unit.members("is_tax_unit_dependent", period)
        )
        # us_govt_interest aggregates all members' person-level inputs by
        # default. Remove dependents' share while retaining a supplied
        # tax-unit government-interest amount.
        government_interest = max_(
            0,
            tax_unit("us_govt_interest", period) - dependent_government_interest,
        )
        gross_investment_income = max_(0, taxable_interest - government_interest)
        gross_investment_income += tax_unit_non_dep_add(
            tax_unit, period, ["ordinary_dividend_income"]
        )
        # Annuities and royalties are not modeled separately.
        long_term_gain = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        short_term_gain = tax_unit_non_dep_add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        # Line 4b.
        net_gain = max_(0, long_term_gain + short_term_gain)
        # Line 4c.
        net_capital_gain = max_(0, long_term_gain + min_(0, short_term_gain))
        # Line 4d. The line 4e election to include net capital gain is not
        # modeled, matching hi_capital_gain_for_alternative_tax.
        net_gain_less_net_capital_gain = net_gain - min_(net_gain, net_capital_gain)
        # Line 5. Modeled investment expenses are miscellaneous expenses on
        # Worksheet A-6 line 25. N-158 requires the smaller of those expenses
        # and the deduction allowed on Worksheet A-6 line 29. The two-percent
        # floor is shared with employee business expenses and tax-prep fees.
        p = parameters(period).gov.irs.deductions.itemized.misc
        investment_expenses = tax_unit_non_dep_add(
            tax_unit, period, ["investment_expenses"]
        )
        misc_expenses = investment_expenses + tax_unit_non_dep_add(
            tax_unit, period, p.sources
        )
        misc_floor = p.floor * max_(0, tax_unit("hi_agi", period))
        allowed_misc_expenses = max_(0, misc_expenses - misc_floor)
        allowed_investment_expenses = min_(investment_expenses, allowed_misc_expenses)
        # Line 6.
        net_investment_income = max_(
            0,
            gross_investment_income
            + net_gain_less_net_capital_gain
            - allowed_investment_expenses,
        )
        # Line 8.
        return min_(interest_expense, net_investment_income)
