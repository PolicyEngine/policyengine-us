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
        # Policy Manual Section 1.6 defines an eligible child by age, custody,
        # and relationship to the applicant -- not by tax-unit dependency, so we
        # gate on age and immigration status only (mirroring WV and AK CCAP).
        p = parameters(period).gov.states["in"].fssa.ccdf.eligibility
        age = person("age", period.this_year)
        # A child over 13 "with appropriately documented special needs or court
        # ordered supervision" who is under 18 at application or reapplication
        # "may participate until the Sunday following their nineteenth (19th)
        # birthday". is_disabled proxies the documented special-needs status
        # (IEP, SSI verification, Head Start, or medical diagnosis per Section
        # 1.6); we do not track the documentation type. Subsidy periods run
        # at least 53 weeks, so a qualifying child is normally reauthorized at
        # 18; we do not track the application date and apply the under-19
        # ceiling to all qualifying children, approximating the Sunday grace
        # with annual age.
        special_status = person("is_disabled", period.this_year) | person(
            "is_under_court_supervision", period.this_year
        )
        age_limit = where(special_status, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
