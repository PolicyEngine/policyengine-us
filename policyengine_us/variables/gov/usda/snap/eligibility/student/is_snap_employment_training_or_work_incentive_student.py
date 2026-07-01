from policyengine_us.model_api import *


class is_snap_employment_training_or_work_incentive_student(Variable):
    value_type = bool
    entity = Person
    label = "SNAP student placed in higher education through an employment and training or work incentive program"
    documentation = (
        "Whether this person was placed in or enrolled in an institution of "
        "higher education through a qualifying employment and training program "
        "(7 CFR 273.5(b)(11)) or work incentive program (7 CFR 273.5(b)(4)). "
        "Single override point for partners; equivalent to either underlying "
        "input being true."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.5#b",
        "https://www.law.cornell.edu/uscode/text/7/2015#e",
    )

    def formula(person, period, parameters):
        employment_training = person("is_snap_employment_training_student", period)
        work_incentive = person("is_snap_work_incentive_student", period)
        return employment_training | work_incentive
