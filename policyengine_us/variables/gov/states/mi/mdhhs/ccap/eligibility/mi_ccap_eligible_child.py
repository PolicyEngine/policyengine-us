from policyengine_us.model_api import *


class mi_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Michigan CDC"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=1"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.ccap.eligibility
        age = person("age", period.this_year)
        # BEM 703: children under 13 are age-eligible; children 13 to under 18
        # who require constant care are also eligible (is_disabled proxy). We
        # don't track court-ordered supervision or the age-18 high-school
        # completion pathway at the moment.
        requires_constant_care = person("is_disabled", period.this_year)
        age_eligible = where(
            requires_constant_care,
            age < p.disabled_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
