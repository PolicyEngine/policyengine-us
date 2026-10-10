from policyengine_us.model_api import *


class MedicaidLTSSSetting(Enum):
    INSTITUTIONAL = "Institutional"
    HCBS = "Home and community-based services"
    UNKNOWN = "Unknown"


class medicaid_ltss_setting(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSSetting
    default_value = MedicaidLTSSSetting.UNKNOWN
    entity = Person
    label = "Medicaid LTSS setting"
    definition_period = MONTH
    documentation = (
        "Explicit setting input for the opt-in Medicaid LTSS financial "
        "threshold screen. INSTITUTIONAL means residence in a nursing "
        "facility or other medical institution for at least 30 consecutive "
        "days; Delaware applies its 250% standard only to nursing facility "
        "residents, so a hospitalized Delaware applicant falls outside the "
        "modeled setting (DSSM 20100.2.2). UNKNOWN is fail-closed. This "
        "input is independent of is_in_medicaid_facility and does not "
        "establish institutional level of care, functional eligibility, "
        "service authorization, or receipt of services."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.236",
        "https://www.law.cornell.edu/cfr/text/42/435.217",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=1",
    )
