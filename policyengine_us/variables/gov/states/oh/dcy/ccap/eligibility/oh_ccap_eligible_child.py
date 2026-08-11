from policyengine_us.model_api import *


class oh_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Ohio CCAP"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-02",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dcy.ccap.eligibility
        age = person("age", period.this_year)
        special_needs = person("oh_ccap_special_needs", period)
        age_eligible = where(
            special_needs,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
