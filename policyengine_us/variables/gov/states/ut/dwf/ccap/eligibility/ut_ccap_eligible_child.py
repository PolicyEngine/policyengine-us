from policyengine_us.model_api import *


class ut_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Utah CCAP eligible child"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-702"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.eligibility
        age = person("age", period.this_year)
        # Children with special needs (R986-700-717) or under court
        # supervision remain eligible through the higher age limit
        # (R986-700-702(5)(b)); is_disabled proxies special-needs status and
        # the court-supervision pathway is not tracked.
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        # The child must be a U.S. citizen, authorized non-citizen, refugee,
        # or permanent resident (R986-700-702); this matches the federal CCDF
        # immigration test, and the parent's immigration status is not
        # considered. The requirement that the child need at least eight
        # hours of care per month (R986-700-702) is not modeled.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
