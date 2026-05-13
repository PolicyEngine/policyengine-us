from policyengine_us.model_api import *


class ut_ui_weekly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "Utah UI weekly hours worked while claiming"
    unit = "hour"
    definition_period = YEAR
    default_value = 0
    reference = "https://jobs.utah.gov/ui/jobseeker/claimantguide.pdf#page=13"
    # Hours worked during a claim week. A claimant who works at least the
    # full-time hours threshold (40 hours) in a week is not eligible for
    # benefits that week per Utah DWS Claimant Guide page 11 (PDF file p. 13)
    # and the "total unemployment" definition in Utah Code § 35A-4-207.
