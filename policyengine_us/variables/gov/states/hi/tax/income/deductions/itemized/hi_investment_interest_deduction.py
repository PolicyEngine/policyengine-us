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
        "https://files.hawaii.gov/tax/forms/2025/n158_i.pdf",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # Line 3. The line 2 carryforward from the prior year is not modeled.
        interest_expense = add(tax_unit, period, ["investment_interest_expense"])
        # Line 4a: interest and ordinary dividends. Annuities and royalties are
        # not modeled separately.
        gross_investment_income = add(
            tax_unit,
            period,
            ["taxable_interest_income", "ordinary_dividend_income"],
        )
        long_term_gain = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        short_term_gain = add(tax_unit, period, ["short_term_capital_gains"])
        # Line 4b.
        net_gain = max_(0, long_term_gain + short_term_gain)
        # Line 4c.
        net_capital_gain = max_(0, long_term_gain + min_(0, short_term_gain))
        # Line 4d. The line 4e election to include net capital gain is not
        # modeled, matching hi_capital_gain_for_alternative_tax.
        net_gain_less_net_capital_gain = net_gain - min_(net_gain, net_capital_gain)
        # Line 5.
        investment_expenses = add(tax_unit, period, ["investment_expenses"])
        # Line 6.
        net_investment_income = max_(
            0,
            gross_investment_income
            + net_gain_less_net_capital_gain
            - investment_expenses,
        )
        # Line 8.
        return min_(interest_expense, net_investment_income)
