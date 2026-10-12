from policyengine_us.model_api import *


class wi_cts_dependent_care_deduction(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS allowed dependent care deduction"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Childcare cost per care recipient. Override with verified work-related care costs or incapacitated-adult care, subject to Handbook 3.2.1.2.3 limits."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        limit = where(
            person("age", period.this_year) < p.care_young_age,
            p.care_young_limit,
            p.care_other_limit,
        )
        return min_(max_(person("pre_subsidy_childcare_expenses", period), 0), limit)
