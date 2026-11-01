from policyengine_us.model_api import *


class md_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Maryland Child Care Scholarship (CCS)"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.02#B(11)",
        "https://web.archive.org/web/20220121165420id_/https://earlychildhood.marylandpublicschools.org/system/files/filedepot/3/2018_maryland_state_plan.pdf#page=81",
        "https://web.archive.org/web/20241110153119id_/https://earlychildhood.marylandpublicschools.org/system/files/filedepot/12/ffy2022_2024_ccdf_plan_approved.pdf#page=87",
        "https://earlychildhood.marylandpublicschools.org/system/files/filedepot/3/final_fy_2022_-_2024_ccdf_online_draft_.pdf#page=62",
        "https://earlychildhood.marylandpublicschools.org/system/files/filedepot/12/acf-118_ccdf_ffy_2025-2027_plan_approved_updated_6.25.25_amendment_request_1.pdf#page=23",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        # NOTE: COMAR 13A.14.06.02B(11) defines older children through
        # disability only; the court route follows the CCDF plan election.
        # Each route only extends the ordinary ceiling, so a child meeting
        # both routes gets the higher ceiling.
        disabled_age_limit = where(is_disabled, p.disabled_child, p.child)
        court_age_limit = where(court_supervision, p.court_supervised_child, p.child)
        age_limit = max_(disabled_age_limit, court_age_limit)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return (age < age_limit) & immigration_eligible
