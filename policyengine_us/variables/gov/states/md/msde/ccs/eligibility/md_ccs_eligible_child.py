from policyengine_us.model_api import *


class md_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Maryland Child Care Scholarship (CCS)"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.02",
        "https://earlychildhood.marylandpublicschools.org/system/files/filedepot/12/acf-118_ccdf_ffy_2025-2027_plan_approved_updated_6.25.25_amendment_request_1.pdf#page=23",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child, p.child)
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible

    def formula_2024_10_01(person, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        # Approved FFY 2025-2027 plan 2.2.1(b)-(c): both routes include
        # age 18, ending at 19. COMAR's child definition still omits the
        # court route; use the approved plan from its current period start.
        age_limit = where(is_disabled | court_supervision, p.disabled_child, p.child)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return (age < age_limit) & immigration_eligible
