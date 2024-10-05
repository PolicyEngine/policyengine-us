from policyengine_us.model_api import *


class is_in_k12_school(Variable):
    value_type = bool
    entity = Person
    label = "Is in a K-12 school"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        # Assume that people aged 5-17 are in school.
        # Not parameterized because this is an imputation rather than a policy
        # rule.
        MIN_AGE = 5
        MAX_AGE = 17
        return (age >= MIN_AGE) & (age <= MAX_AGE)
