from policyengine_us.model_api import *


class MedicaidLTSSSetting(Enum):
    UNKNOWN = "Unknown"
    INSTITUTIONAL = "Institutional"
    HCBS = "Home and community-based services"


class medicaid_ltss_setting(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSSetting
    default_value = MedicaidLTSSSetting.UNKNOWN
    entity = Person
    label = "Medicaid LTSS setting"
    definition_period = MONTH
    documentation = (
        "Explicit setting input for the opt-in Medicaid LTSS financial "
        "threshold screen. UNKNOWN is fail-closed. This input does not "
        "establish institutional level of care, functional eligibility, "
        "service authorization, or receipt of services."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.236",
        "https://www.law.cornell.edu/cfr/text/42/435.217",
    )
