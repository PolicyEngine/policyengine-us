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
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.gross_income
        total = add(person, period, p.non_negative_sources)
        # Loss-eligible categories per N.J.S. 54A:5-1: each is
        # summed within the category then clamped to $0.
        cats = p.loss_eligible_categories
        total = total + max_(add(person, period, cats.category_b), 0)
        total = total + max_(add(person, period, cats.category_c), 0)
        total = total + max_(add(person, period, cats.category_d), 0)
        total = total + max_(add(person, period, cats.category_h), 0)
        total = total + max_(add(person, period, cats.category_k_p), 0)
        # A claim of right repayment offsets income of its own category,
        # not below zero (N.J.S.A. 54A:5-2).
        return total - person("nj_claim_of_right_offset", period)
