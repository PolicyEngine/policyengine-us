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
        # Children 13 and older with documented special needs remain eligible
        # until the age limit. Court-ordered supervision is another extension
        # pathway that we don't track at the moment.
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible
