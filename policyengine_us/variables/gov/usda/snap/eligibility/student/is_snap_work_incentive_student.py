from policyengine_us.model_api import *


class is_snap_work_incentive_student(Variable):
    value_type = bool
    entity = Person
    label = "SNAP student enrolled in higher education through a work incentive program"
    documentation = (
        "Whether this person was enrolled in an institution of higher "
        "education as a result of participation in a work incentive program "
        "under title IV of the Social Security Act (the Job Opportunities and "
        "Basic Skills program or its TANF successor). Mere participation in a "
        "work program does not qualify: the enrollment must result from the "
        "program."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.5#b_4",
        "https://www.law.cornell.edu/uscode/text/7/2015#e_7",
    )
