from policyengine_us.model_api import *


class ca_child_exemption_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California child exemption amount"
    documentation = (
        "https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html"
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        head = person("is_tax_unit_head", period)
        lower_age_threshold = person("age", period) < p.age_threshold.lower
        income = person("earned_income", period)
        support_costs = person("care_and_support_costs", period)

        income_rate = np.zeros_like(support_costs)
        mask = support_costs != 0
        income_rate[mask] = income[mask] / support_costs[mask]
        income_rate_eligible = income_rate < 0.5
        student_no_income = (
            person("is_full_time_student", period)
            & income_rate_eligible
            & (person("age", period) < p.age_threshold.upper)
        )

        return head & (
            lower_age_threshold | income_rate_eligible | student_no_income
        )
