from policyengine_us.model_api import *


class ct_c4k_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Eligible child for Connecticut Care 4 Kids"
    reference = (
        "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-04/",
        "https://www.cga.ct.gov/2020/rpt/pdf/2020-R-0274.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.special_needs_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible
