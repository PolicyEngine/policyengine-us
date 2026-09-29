from policyengine_us.model_api import *


class wv_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for West Virginia CCAP"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=25",
        "https://bfa.wv.gov/media/39915/download?inline#page=17",
    )

    def formula(person, period, parameters):
        # Sections 3.1.2.1 and 3.1.2.2 allow ages 13-17 under court
        # supervision or with special needs, respectively.
        p = parameters(period).gov.states.wv.dhhr.ccap.eligibility
        age = person("age", period.this_year)
        has_developmental_delay = person("has_developmental_delay", period.this_year)
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = where(
            has_developmental_delay | under_court_supervision,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
