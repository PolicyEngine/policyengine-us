from policyengine_us.model_api import *


class sc_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for South Carolina CCAP"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=14",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=19",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.dss.ccap.eligibility
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(
            is_disabled,
            age < p.disabled_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
