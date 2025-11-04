from policyengine_us.model_api import *


class nj_total_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey total income by person"
    unit = USD
    documentation = "Total income calculated from specific income categories per NJ statute, before exclusions. This is built from gross income sources, not federal AGI."
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",  # Lines 15-27
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # Build NJ total income from specific income categories per NJ statute 54A:5-1
        # This corresponds to lines 15-27 on Form NJ-1040
        return add(
            person,
            period,
            [
                "employment_income",  # Line 15: Wages, salaries, tips (Category a)
                "taxable_interest_income",  # Line 16a: Interest (Category e)
                "dividend_income",  # Line 17: Dividends (Category f)
                "self_employment_income",  # Line 18: Net business profits (Category b)
                "farm_income",  # Line 18: Farm income (Category b)
                "long_term_capital_gains",  # Line 19: Long-term capital gains (Category c)
                "short_term_capital_gains",  # Line 19: Short-term capital gains (Category c)
                "taxable_pension_income",  # Line 20a: Pensions (Category j)
                "taxable_ira_distributions",  # Line 20a: IRA distributions (Category j)
                "partnership_s_corp_income",  # Lines 21-22: Partnership & S-corp (Categories k, p)
                "rental_income",  # Line 23: Rents, royalties (Category d)
                "gambling_winnings",  # Line 24: Gambling (Category g)
                "alimony_income",  # Line 25: Alimony received (Category n)
                "miscellaneous_income",  # Line 26: Other income
            ],
        )
