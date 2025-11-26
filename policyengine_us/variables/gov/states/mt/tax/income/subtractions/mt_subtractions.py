from policyengine_us.model_api import *


class mt_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Montana subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2110/",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=5",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions
        total_subtractions = add(person, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
