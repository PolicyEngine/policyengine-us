from policyengine_us.model_api import *


class nh_ssp_ineligible_child(Variable):
    value_type = bool
    entity = Person
    label = "New Hampshire adult assistance ineligible child"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = (
        "An SSI-ineligible child whom New Hampshire also counts when it "
        "allocates parental income: under 18, or under 20 while a full-time "
        "student in a secondary school or equivalent training. An older "
        "college student gets no allocation."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ssp.ineligible_child
        year = period.this_year
        age = person("age", year)
        # He-W 652.03(h)(1): a sibling "under the age of 20 if a full-time
        # student in a secondary school", including equivalent vocational or
        # technical training. is_in_secondary_school covers that training.
        secondary_student = (
            person("is_full_time_student", year)
            & person("is_in_secondary_school", year)
            & (age < p.secondary_student_age_limit)
        )
        in_scope = (age < p.age_limit) | secondary_student
        return person("is_ssi_ineligible_child", period) & in_scope
