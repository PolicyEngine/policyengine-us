from policyengine_us.model_api import *


class md_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Maryland Child Care Scholarship (CCS)"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.02",
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
        age_limit = select(
            [is_disabled, court_supervision],
            [p.disabled_child, p.court_supervised_child],
            default=p.child,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return (age < age_limit) & immigration_eligible
