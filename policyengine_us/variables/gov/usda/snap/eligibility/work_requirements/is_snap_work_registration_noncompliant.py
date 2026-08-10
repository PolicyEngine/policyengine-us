from policyengine_us.model_api import *


class is_snap_work_registration_noncompliant(Variable):
    value_type = bool
    entity = Person
    label = "SNAP work registration noncompliant"
    definition_period = MONTH
    default_value = False
    documentation = "Whether a non-exempt SNAP work registrant has affirmatively failed to comply with SNAP work requirements without good cause (refusing suitable employment, employment and training program noncompliance, or voluntarily quitting a job or reducing work effort under 7 CFR 273.7(j)). These State-agency 'without good cause' determinations are not observable in survey data, so the baseline assumes compliance (false). Set true to model work-registration sanctions under 7 CFR 273.7(f)(1)-(2)."
    reference = (
        "https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-C/part-273/subpart-E/section-273.7#p-273.7(f)",
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title7-section2015&num=0&edition=prelim",
    )
