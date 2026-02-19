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
        # Loss-eligible categories per N.J.S. 54A:5-1: each is
        # summed within the category then clamped to $0.
        cats = p.loss_eligible_categories
        for cat in cats:
            total += max_(add(person, period, cats[cat]), 0)
        return total
