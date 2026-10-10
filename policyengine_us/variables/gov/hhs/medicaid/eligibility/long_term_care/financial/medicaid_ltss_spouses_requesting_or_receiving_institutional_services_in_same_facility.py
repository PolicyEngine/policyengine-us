from policyengine_us.model_api import *


class medicaid_ltss_spouses_requesting_or_receiving_institutional_services_in_same_facility(
    Variable
):
    value_type = bool
    entity = MaritalUnit
    label = "Both spouses request or receive Medicaid LTSS institutional services in the same facility"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Whether both spouses request or receive institutional services and "
        "reside, or will reside, in the same facility. This includes a "
        "current recipient whose spouse requests services at that facility. "
        "It records the service and location facts used by Delaware DSSM "
        "20810; it does not choose an assistance unit or establish service "
        "eligibility. Defaults to false when these facts are not supplied."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67"
