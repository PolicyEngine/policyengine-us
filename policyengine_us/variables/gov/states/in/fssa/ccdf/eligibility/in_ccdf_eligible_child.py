from policyengine_us.model_api import *


class in_ccdf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Indiana CCDF eligible child"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=12"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.eligibility
        age = person("age", period.this_year)
        # The documented special-needs proxy is retained. Section 1.6 uses
        # the same application-age and continuation rules for both pathways.
        special_status = person("is_disabled", period.this_year) | person(
            "is_under_court_supervision", period.this_year
        )
        continuing_award = person("in_ccdf_has_active_under_18_award", period)
        special_age_eligible = (age < p.special_needs_application_age_limit) | (
            continuing_award & (age < p.disabled_child_age_limit)
        )
        # The Sunday-after-19th-birthday grace cannot be resolved with annual
        # age, so the existing exclusive age-19 continuation ceiling remains.
        age_eligible = (age < p.child_age_limit) | (
            special_status & special_age_eligible
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
