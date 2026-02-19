from policyengine_us.model_api import *


class nj_gross_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.gross_income
        total = add(person, period, p.non_negative_sources)
        # Loss-eligible categories per N.J.S. 54A:5-1: each group
        # is summed then clamped to $0 (same-category rule).
        loss_eligible_categories = [
            # (b) Business profits - Line 18
            ["self_employment_income", "farm_income"],
            # (c) Capital gains - Line 19
            ["short_term_capital_gains", "long_term_capital_gains"],
            # (d) Rent and royalties - Line 23
            ["rental_income"],
            # (k, p) Partnership and S-corp - Lines 21-22
            ["partnership_s_corp_income"],
        ]
        for cat in loss_eligible_categories:
            total += max_(add(person, period, cat), 0)
        return total
