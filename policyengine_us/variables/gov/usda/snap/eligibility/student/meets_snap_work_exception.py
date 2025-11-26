from policyengine_us.model_api import *


class meets_snap_work_exception(Variable):
    value_type = bool
    entity = Person
    label = "Meets SNAP student work exception"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2015#e_4"

    def formula(person, period, parameters):
        # Exception 4: Employed at least 20 hours per week or work-study
        hours_worked = person("weekly_hours_worked_before_lsr", period)
        p = parameters(period).gov.usda.snap.student
        meets_hours_requirement = hours_worked >= p.working_hours_threshold

        # Or participating in federal/state work-study
        participates_in_work_study = person(
            "is_federal_work_study_participant", period
        )

        return meets_hours_requirement | participates_in_work_study
