from policyengine_us.model_api import *


class tn_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Tennessee CCAP"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=23"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.eligibility
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # NOTE: Court-supervision eligibility awaits a general input variable.
        age_eligible = where(
            is_disabled,
            age < p.special_needs_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
