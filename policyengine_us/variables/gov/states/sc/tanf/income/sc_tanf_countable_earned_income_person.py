from policyengine_us.model_api import *


class sc_tanf_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=130"  # Section 8.12

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned.disregard
        gross_earned_income = person("sc_tanf_gross_earned_income", period)
        month = period.start.month

        # First 4 months (Jan-Apr): 50% disregard
        # Remaining 8 months (May-Dec): $100 flat disregard
        # Use calendar months as a proxy. The actual policy refers to
        # "first 4 months of employment" which cannot be tracked.
        initial_period = month <= p.percentage.months
        initial_countable = gross_earned_income * (1 - p.percentage.rate)
        ongoing_countable = max_(gross_earned_income - p.amount, 0)

        return where(initial_period, initial_countable, ongoing_countable)
