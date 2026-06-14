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
        # Children 13 and older with documented special needs remain eligible
        # until the age limit. Court-ordered supervision is another extension
        # pathway that we don't track at the moment.
        p = parameters(period).gov.states["in"].fssa.ccdf.eligibility
        age = person("age", period.this_year)
        # is_disabled proxies the Manual's documented special-needs status (IEP,
        # SSI verification, Head Start, or medical diagnosis per Section 1.6);
        # we don't track the specific documentation type at the moment.
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
