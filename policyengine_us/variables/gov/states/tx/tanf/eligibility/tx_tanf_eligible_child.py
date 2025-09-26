from policyengine_us.model_api import *


class tx_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Texas TANF eligible child"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf"
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        is_full_time_student = person("is_full_time_student", period)

        # Child under 18
        under_18 = age < 18

        # Or 18 and a full-time student expected to graduate before turning 19
        student_18 = (age == 18) & is_full_time_student

        return under_18 | student_18
