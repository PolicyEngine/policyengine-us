from policyengine_us.model_api import *


class il_hbi_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in Illinois Health Benefits for Immigrants"
    definition_period = YEAR
    defined_for = StateCode.IL
    documentation = """
    Whether a person is currently enrolled in Illinois Health Benefits for
    Immigrants. This is an input variable because enrollment depends on
    whether a person enrolled before enrollment freezes took effect.

    Key dates:
    - HBIA (adults 42-64): New enrollment paused July 1, 2023; program ended July 1, 2025
    - HBIS (seniors 65+): New enrollment paused November 6, 2023; existing enrollees can renew
    - All Kids (children 0-18): Enrollment remains open
    """
