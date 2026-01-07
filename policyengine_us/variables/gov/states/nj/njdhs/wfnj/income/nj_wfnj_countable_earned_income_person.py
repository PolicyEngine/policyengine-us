from policyengine_us.model_api import *


class nj_wfnj_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "New Jersey WFNJ countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-8"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.wfnj.income
        gross_earned = person("tanf_gross_earned_income", period)
        month = period.start.month

        # Calendar month proxy for enrollment months (assuming ≥20 hrs/week).
        # N.J.A.C. 10:90-3.8 provides tiered disregards based on months enrolled.
        # Use calendar months as a proxy:
        # - January (month 1): 100% disregard
        # - February-July (months 2-7): 75% disregard
        # - August-December (months 8-12): 50% disregard
        disregard_rate = p.earned_income_disregard.calc(month)
        return gross_earned * (1 - disregard_rate)
