from policyengine_us.model_api import *


class nj_gross_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey gross income"
    unit = USD
    documentation = (
        "Gross income calculated from specific income categories per NJ "
        "statute, before additions and subtractions. Under the 'same "
        "category rule' (N.J.S. 54A:5-1), if any income category has a net "
        "loss, that loss is disregarded (treated as $0) and cannot offset "
        "income from other categories."
    )
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # Income sources that cannot go negative (always >= 0)
        non_negative_sources = [
            "employment_income",
            "taxable_interest_income",
            "dividend_income",
            "taxable_pension_income",
            "taxable_ira_distributions",
            "gambling_winnings",
            "alimony_income",
            "miscellaneous_income",
        ]

        # Sum non-negative sources directly
        total = sum(person(source, period) for source in non_negative_sources)

        # Category c: Capital gains (short-term + long-term combined)
        # Apply same-category rule: if net is negative, treat as 0
        capital_gains = person("short_term_capital_gains", period) + person(
            "long_term_capital_gains", period
        )
        total += max_(capital_gains, 0)

        # Category b: Business/self-employment income (includes farm)
        # Each can go negative but losses cannot offset other categories
        self_employment = person("self_employment_income", period)
        total += max_(self_employment, 0)

        farm = person("farm_income", period)
        total += max_(farm, 0)

        # Categories k, p: Partnership and S-corp income
        partnership_s_corp = person("partnership_s_corp_income", period)
        total += max_(partnership_s_corp, 0)

        # Category d: Rental income (rents, royalties)
        rental = person("rental_income", period)
        total += max_(rental, 0)

        return total
