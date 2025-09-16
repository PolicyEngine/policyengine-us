from policyengine_us.model_api import *


class dc_medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in DC Medicaid/Alliance"
    definition_period = YEAR
    defined_for = StateCode.DC
    default_value = False
    reference = [
        "https://dhcf.dc.gov/alliance",
    ]
    documentation = (
        "Indicates whether the person is currently enrolled in DC Medicaid "
        "or Alliance program. Used to grandfather existing enrollees when "
        "eligibility rules change."
    )
