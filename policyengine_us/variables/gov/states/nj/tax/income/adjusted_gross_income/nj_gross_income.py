from policyengine_us.model_api import *


class nj_gross_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf#page=1",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # NJ "Same Category Rule": Net losses within any income category must be
        # disregarded (capped at $0) - losses cannot offset income from other categories.
        # Per N.J.S. 54A:5-1, the 16 income categories are treated separately.

        # Category (a): Wages, salaries, tips - always positive
        cat_a = person("employment_income", period)

        # Category (b): Net profits from business (self-employment + farm)
        cat_b = max_(
            person("self_employment_income", period)
            + person("farm_income", period),
            0,
        )

        # Category (c): Net gains from disposition of property (capital gains)
        cat_c = max_(
            person("short_term_capital_gains", period)
            + person("long_term_capital_gains", period),
            0,
        )

        # Category (d): Net rents, royalties, patents, copyrights
        cat_d = max_(person("rental_income", period), 0)

        # Category (e): Interest income
        cat_e = person("taxable_interest_income", period)

        # Category (f): Dividends
        cat_f = person("dividend_income", period)

        # Category (g): Gambling winnings
        cat_g = person("gambling_winnings", period)

        # Category (j): Pensions and annuities (including IRA distributions)
        cat_j = person("taxable_pension_income", period) + person(
            "taxable_ira_distributions", period
        )

        # Categories (k) and (p): Partnership and S-corp income
        # These are combined in our data model
        cat_k_p = max_(person("partnership_s_corp_income", period), 0)

        # Category (n): Alimony
        cat_n = person("alimony_income", period)

        # Other income (Line 26)
        cat_other = person("miscellaneous_income", period)

        return (
            cat_a
            + cat_b
            + cat_c
            + cat_d
            + cat_e
            + cat_f
            + cat_g
            + cat_j
            + cat_k_p
            + cat_n
            + cat_other
        )
