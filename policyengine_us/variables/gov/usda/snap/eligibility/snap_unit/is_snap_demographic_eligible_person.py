from policyengine_us.model_api import *


class is_snap_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person in SNAP unit based on demographics"
    definition_period = YEAR

    def formula(person, period, parameters):
        ineligible_student = person("is_snap_ineligible_student", period)
        work_requirements_eligible = person(
            "meets_snap_work_requirements_person", period
        )
        immigration_status_eligible = person(
            "snap_immigration_status_eligible_person", period
        )

        return (
            ~ineligible_student
            & work_requirements_eligible
            & immigration_status_eligible
        )
