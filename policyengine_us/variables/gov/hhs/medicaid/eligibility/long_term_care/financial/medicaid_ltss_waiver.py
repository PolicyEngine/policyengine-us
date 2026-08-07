from policyengine_us.model_api import *


class MedicaidLTSSWaiver(Enum):
    NONE = "None"
    WA_COPES = "Washington COPES"
    WA_NEW_FREEDOM = "Washington New Freedom"
    WA_RSW = "Washington Residential Support Waiver"
    UNKNOWN = "Unknown"


class medicaid_ltss_waiver(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSWaiver
    default_value = MedicaidLTSSWaiver.NONE
    entity = Person
    label = "Medicaid LTSS waiver"
    definition_period = MONTH
    documentation = (
        "Explicit named-waiver input for the opt-in Medicaid LTSS financial "
        "threshold screen. UNKNOWN and unsupported waiver selections are "
        "unmodeled and fail closed; they never inherit a generic statewide "
        "HCBS rule. This input does not establish waiver enrollment, a slot, "
        "level of care, or service authorization."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.217",
        "https://www.hca.wa.gov/free-or-low-cost-health-care/i-help-others-apply-and-access-apple-health/wac-182-515-1505-home-and-community-based-hcb-waiver-services-authorized-home-and-community-services-hcs",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-515-1508",
    )
