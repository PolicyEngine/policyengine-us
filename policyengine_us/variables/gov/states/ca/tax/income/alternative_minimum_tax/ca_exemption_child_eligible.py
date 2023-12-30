from policyengine_us.model_api import *


class ca_exemption_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California Minimum exemption amount"
    documentation = (
        "https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html"
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        head = person("is_tax_unit_head", period)
        child = person("age", period) < p.age_threshold.lower
        no_income = (person("age", period) == p.age_threshold.lower) & (
            person("earned_income", period) == 0
        )
        student_no_income = (
            person("is_full_time_student", period)
            & (person("earned_income", period) == 0)
            & (person("age", period) < p.age_threshold.upper)
        )

        return head & (child | no_income | student_no_income)
