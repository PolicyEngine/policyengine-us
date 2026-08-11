from policyengine_us.model_api import *


class is_snap_abawd_in_good_faith_exemption_window(Variable):
    value_type = bool
    entity = Person
    label = "Person is in a SNAP ABAWD good-faith-effort exemption window"
    definition_period = MONTH
    documentation = (
        "Whether the person's State is in an approved good-faith-effort "
        "exemption window under 7 U.S.C. 2015(o)(7). During such a window a "
        "noncontiguous State temporarily retains a specified set of pre-HR1 "
        "ABAWD exceptions on top of the post-HR1 exception set (handled in "
        "meets_snap_abawd_work_requirements and meets_snap_work_requirements_"
        "person). Alaska is currently the only State with an approved window "
        "(2025-11-01 through 2026-10-31); add other States here as they are "
        "approved."
    )
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title7-section2015&num=0&edition=prelim",
        "https://health.alaska.gov/en/education/hr-1-ak-impacts/",
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period.this_year)
        ak = parameters(
            period
        ).gov.states.ak.dpa.snap.work_requirements.abawd.good_faith_exemption.in_effect
        return select(
            [state_code == StateCode.AK],
            [ak],
            default=False,
        )
