from policyengine_us.model_api import *


class ut_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Utah CCAP eligible child"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-702",
        "https://jobs.utah.gov/occ/provider/r986700.pdf#page=2",
        "https://jobs.utah.gov/customereducation/services/childcare/occsubsidyfact.pdf#page=1",
        "https://jobs.utah.gov/occ/ccdfplan.pdf#page=19",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.eligibility
        age = person("age", period.this_year)
        # R986-700-702(5)(b) extends the age limit for children under court
        # supervision or meeting R986-700-717 special-needs requirements.
        # is_disabled proxies the latter, without assigning it to court cases.
        # The r986700.pdf edition (last changed March 31, 2022) numbers this
        # rule (4)(b); State Plan FFY 2025-2027 2.2.1(b)-(c) also covers it.
        is_disabled = person("is_disabled", period.this_year)
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(
            is_disabled | under_court_supervision,
            p.disabled_child_age_limit,
            p.child_age_limit,
        )
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
