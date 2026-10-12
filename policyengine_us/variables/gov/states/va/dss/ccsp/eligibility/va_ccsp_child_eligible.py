from policyengine_us.model_api import *


class va_ccsp_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Virginia Child Care Subsidy Program"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section20/",
        "https://ris.dls.virginia.gov/uploads/22VAC40/dibr/VDOE%20Child%20Care%20Program%20Guidance%20Manual%205.3.2023-20240822104447.pdf#page=52",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # 8VAC20-790-20(A)(1) and Guidance Manual 3.3 G: a child under court
        # supervision shares the incapacity ceiling.
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(is_disabled | court_supervision, p.disabled_child, p.child)
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
