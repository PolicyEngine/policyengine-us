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
        # Income sources that cannot go negative (always >= 0).
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
        total = sum(person(source, period) for source in non_negative_sources)

        # Categories that can have losses. Under the same-category rule
        # (N.J.S. 54A:5-1), if a category's net is negative it is
        # disregarded (treated as $0) and cannot offset other categories.
        # Each inner list is summed first, then clamped to zero.
        loss_eligible_categories = [
            # Category c: capital gains (short + long combined)
            ["short_term_capital_gains", "long_term_capital_gains"],
            # Category b: self-employment
            ["self_employment_income"],
            # Category b: farm
            ["farm_income"],
            # Categories k, p: partnership & S-corp
            ["partnership_s_corp_income"],
            # Category d: rental / royalties
            ["rental_income"],
        ]
        for category_sources in loss_eligible_categories:
            category_total = sum(
                person(source, period) for source in category_sources
            )
            total += max_(category_total, 0)

        return total
