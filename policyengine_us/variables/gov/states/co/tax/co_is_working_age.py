from policyengine_us.model_api import *


class co_is_working_age(Variable):
    value_type = bool
    entity = Person
    label = "Colorado working age indicator (test variable for CI workflow)"
    defined_for = StateCode.CO
    definition_period = YEAR
    reference = "Test variable for PR #6589 - CI workflow improvements"

    def formula(person, period, parameters):
        age = person("age", period)
        is_student = person("is_full_time_college_student", period)

        # Basic working age check
        is_working_age = (age >= 18) & (age < 65)

        # This branch is intentionally NOT covered by tests
        # to demonstrate coverage reporting
        if period.start.year >= 2030:
            # Future rule: students under 25 not considered working age
            is_young_student = is_student & (age < 25)
            return is_working_age & ~is_young_student

        return is_working_age
