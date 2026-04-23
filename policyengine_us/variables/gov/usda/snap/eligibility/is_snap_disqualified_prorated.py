from policyengine_us.model_api import *


class is_snap_disqualified_prorated(Variable):
    value_type = bool
    entity = Person
    label = "SNAP disqualified with prorated treatment"
    documentation = (
        "Whether this person is excluded from the SNAP unit under the "
        "'prorated' treatment of 7 CFR 273.11(c)(2) / (c)(3): the "
        "individual's income is divided evenly among all household "
        "members and only the share that would have gone to eligible "
        "members is counted, while resources continue to count in full. "
        "Applies to ineligible students (higher education) and members "
        "who are not immigration-status eligible."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_2"

    def formula(person, period, parameters):
        ineligible_student = person("is_snap_ineligible_student", period)
        immigration_ineligible = ~person(
            "is_snap_immigration_status_eligible", period
        )
        return ineligible_student | immigration_ineligible
