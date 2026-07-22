from policyengine_us.model_api import *


class is_snap_excluded_member(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "SNAP excluded member"
    documentation = (
        "Whether this person is a nonhousehold member or an ineligible "
        "household member excluded from the SNAP unit"
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c",
        "https://www.law.cornell.edu/cfr/text/7/273.11#d",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
    )

    def formula(person, period, parameters):
        return (
            person("is_snap_ineligible_student", period.this_year)
            | ~person("is_snap_immigration_status_eligible", period)
            | ~person("meets_snap_work_requirements_person", period)
        )
