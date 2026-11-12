from policyengine_us.model_api import *


class ny_ccap_accredited_provider(Variable):
    value_type = bool
    entity = Person
    label = "New York CCAP nationally accredited provider"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records whether a nationally recognized child care organization has "
        "accredited the child's licensed or registered provider, under 18 "
        "NYCRR 415.9 and 24-OCFS-LCM-22. "
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
    )
