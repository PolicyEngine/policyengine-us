from policyengine_us.model_api import *


class medicare_part_d_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in Medicare Part D"
    documentation = (
        "Whether the person is enrolled in Medicare Part D. Only a Part D "
        "eligible individual, one entitled to Part A or enrolled in Part B "
        "(medicare_enrolled), can enroll."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1395w-101#a_3_A"
    defined_for = "medicare_enrolled"
    adds = ["takes_up_medicare_part_d_if_eligible"]
