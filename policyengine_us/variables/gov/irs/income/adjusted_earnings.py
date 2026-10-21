from policyengine_us.model_api import *


class adjusted_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Personal earned income adjusted for self-employment tax"
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - p.self_emp_tax_adj)
            * p.employer_share
            * person("self_employment_tax", period)
        )
        # Disability pay reported as wages is earned income (Pub. 503 (2024),
        # file page 4).
        earnings = add(person, period, ["earned_income", "earned_disability_benefits"])
        return max_(0, earnings - adjustment)
