from policyengine_us.model_api import *


class ny_ccap_special_needs_care(Variable):
    value_type = bool
    entity = Person
    label = "New York CCAP parent demonstrates additional special needs care"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records whether the parent or caretaker has demonstrated to the "
        "district that the child needs child care services beyond those "
        "children of similar age generally require, under 18 NYCRR 415.9 and "
        "24-OCFS-LCM-22. The rate also requires disability and expenses "
        "exceeding the regular market rate. "
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=7",
    )
