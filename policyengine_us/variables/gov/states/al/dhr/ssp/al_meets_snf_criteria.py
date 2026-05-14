from policyengine_us.model_api import *


class al_meets_snf_criteria(Variable):
    value_type = bool
    entity = Person
    label = "Alabama SSP recipient meets skilled nursing facility criteria"
    definition_period = MONTH
    defined_for = StateCode.AL
    default_value = False
    reference = (
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9",
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=14",
    )
    documentation = """
    Alabama requires post-October 1, 1986 specialized Independent Homelife Care
    cases to satisfy the skilled nursing facility criteria in Ala. Admin. Code
    r. 660-2-4-.28.
    """
