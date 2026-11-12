from policyengine_us.model_api import *


class ny_ccap_nontraditional_hours(Variable):
    value_type = bool
    entity = Person
    label = "New York CCAP care during nontraditional hours"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records whether the child receives care before 6 a.m. or after "
        "7 p.m. Monday through Friday. Any care on Saturday, Sunday, "
        "New Year's Day, Memorial Day, Independence Day, Labor Day, "
        "Thanksgiving Day, or Christmas Day also qualifies under "
        "24-OCFS-LCM-22."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.9",
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=9",
    )
