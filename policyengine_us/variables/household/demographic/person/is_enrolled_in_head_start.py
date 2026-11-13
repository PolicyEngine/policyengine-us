from policyengine_us.model_api import *


class is_enrolled_in_head_start(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in a Head Start or Early Head Start program"
    definition_period = YEAR
    documentation = (
        "Whether this person enrolls in Head Start or Early Head Start. "
        "Enrollment differs from modeled eligibility and hypothetical take-up."
    )
    reference = (
        "https://uscode.house.gov/us/usc/119-124/t42/s1758/#b-12-A-iii",
        "https://uscode.house.gov/us/usc/119-124/t42/s9840/#a-1-B",
    )
