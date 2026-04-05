from policyengine_us.model_api import *


class NHCCAPServiceLevel(Enum):
    FULL_TIME = "Full-time"
    HALF_TIME = "Half-time"
    PART_TIME = "Part-time"


class nh_ccap_service_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = NHCCAPServiceLevel
    default_value = NHCCAPServiceLevel.FULL_TIME
    definition_period = MONTH
    defined_for = StateCode.NH
    label = "New Hampshire Child Care Scholarship Program service level"
    reference = (
        "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.07",
        "https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/bcdhsc-form-2533.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.service_level
        authorized_hours = person.spm_unit("nh_ccap_authorized_activity_hours", period)
        return p.authorized_hours.calc(authorized_hours)
