from policyengine_us.model_api import *


class ok_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma Child Care Subsidy eligible child"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-3",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-5",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.eligibility
        age = person("age", period.this_year)
        # A child is eligible through the day before their 13th birthday; a
        # child with disabilities or under court supervision is eligible
        # through the day before their 19th birthday (OAC 340:40-7-3).
        # is_disabled proxies OAC 340:40-7-3.1 disability verification.
        # The grace period through the next renewal remains unmodeled.
        is_disabled = person("is_disabled", period.this_year)
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(
            is_disabled | under_court_supervision,
            p.disabled_child_age_limit,
            p.child_age_limit,
        )
        age_eligible = age < age_limit
        # Only the child for whom care is requested must meet citizenship
        # and alienage requirements (OAC 340:40-7-5(c)).
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
