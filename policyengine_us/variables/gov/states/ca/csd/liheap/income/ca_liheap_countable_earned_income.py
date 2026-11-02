from policyengine_us.model_api import *


class ca_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "California LIHEAP countable earned income"
    defined_for = StateCode.CA
    # PDF pages 231,240,247,249
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=231"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        earnings = add(person, period, p.earned_sources)
        # The guide deducts the business expenses of paid employees. A minor's
        # earnings are excluded, so a minor's expenses offset nothing.
        job_expenses = person("unreimbursed_business_employee_expenses", period)
        adult = person("age", period) >= p.earned_income_min_age
        return where(adult, earnings - job_expenses, 0)
