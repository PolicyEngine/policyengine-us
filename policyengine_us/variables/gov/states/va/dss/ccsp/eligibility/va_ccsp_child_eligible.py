from policyengine_us.model_api import *


class va_ccsp_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Virginia Child Care Subsidy Program"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section20/",
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=58",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child, p.child)
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
