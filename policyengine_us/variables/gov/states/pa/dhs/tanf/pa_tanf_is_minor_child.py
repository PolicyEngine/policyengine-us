from policyengine_us.model_api import *


class pa_tanf_is_minor_child(Variable):
    value_type = bool
    entity = Person
    label = "Pennsylvania TANF minor child status"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 105, Section 105.2 - TANF Categorical Requirements"
    documentation = "A person is a minor child for PA TANF if they are under age 18, OR age 18 and a full-time student in secondary school or equivalent vocational/technical training. http://services.dpw.state.pa.us/oimpolicymanuals/cash/105_Category/105_2_TANF_Categorical_Requirements.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        age = person("age", period)
        minor_child_age_limit = p.minor_child_age_limit

        # Under the age limit
        is_under_age = age < minor_child_age_limit

        # OR exactly at age limit and full-time student
        is_student_at_limit = (age == minor_child_age_limit) & person(
            "is_full_time_student", period
        )

        return is_under_age | is_student_at_limit
