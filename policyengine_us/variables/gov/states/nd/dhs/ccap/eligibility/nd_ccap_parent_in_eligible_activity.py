from policyengine_us.model_api import *


class nd_ccap_parent_in_eligible_activity(Variable):
    value_type = bool
    entity = Person
    label = "North Dakota CCAP parent in an eligible activity"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        # Allowable activities include employment, self-employment, education
        # or training, high school or GED completion, and work-study or
        # internship; there is no minimum number of working hours, since
        # activity is documented through proof of income (400-28-55-05). A
        # parent qualifies with positive wages, nonzero self-employment income
        # (a business loss still evidences active self-employment), full-time
        # student status, or TANF enrollment. A disabled caretaker also
        # establishes a child care need: in a one-caretaker household child
        # care is allowed when the caretaker is disabled, and in a
        # two-caretaker household when one caretaker is in an activity and the
        # other is disabled (Incapacity of a Caretaker/Child 400-28-35-15).
        # We do not capture not-yet-paid new employment or active job search at
        # the moment.
        has_earnings = (person("employment_income", period) > 0) | (
            person("self_employment_income", period) != 0
        )
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        is_tanf_enrolled = person.spm_unit("is_tanf_enrolled", period)
        return has_earnings | is_student | is_disabled | is_tanf_enrolled
