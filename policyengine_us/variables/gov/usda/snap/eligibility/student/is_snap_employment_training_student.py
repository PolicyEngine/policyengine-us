from policyengine_us.model_api import *


class is_snap_employment_training_student(Variable):
    value_type = bool
    entity = Person
    label = "SNAP student placed in higher education through an employment and training program"
    documentation = (
        "Whether this person was placed in an institution of higher education "
        "through a qualifying employment and training program (WIOA, a SNAP "
        "E&T program, the Trade Act, or a state or local program). Mere "
        "enrollment in college or in unrelated job training does not qualify: "
        "the placement must come through the program."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.5#b_11",
        "https://www.law.cornell.edu/uscode/text/7/2015#e_3",
    )
