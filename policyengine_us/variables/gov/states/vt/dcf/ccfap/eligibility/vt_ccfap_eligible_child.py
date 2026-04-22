from policyengine_us.model_api import *


class vt_ccfap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Eligible child for Vermont CCFAP"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=4",
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.ccfap.age_threshold
        age = person("age", period.this_year)
        has_special_needs = person("is_disabled", period.this_year)
        age_limit = where(has_special_needs, p.special_needs, p.base)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible
