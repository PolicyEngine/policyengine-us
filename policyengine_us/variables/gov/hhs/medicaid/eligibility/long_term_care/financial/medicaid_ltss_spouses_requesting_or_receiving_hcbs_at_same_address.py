from policyengine_us.model_api import *


class medicaid_ltss_spouses_requesting_or_receiving_hcbs_at_same_address(Variable):
    value_type = bool
    entity = MaritalUnit
    label = "Both spouses request or receive Medicaid LTSS HCBS at the same address"
    definition_period = MONTH
    default_value = False
    documentation = (
        "Whether both spouses request or receive home and community-based "
        "services and reside at the same address. This includes a current "
        "recipient whose spouse requests HCBS. This is the service and "
        "location fact used by Delaware DSSM 20810, independent of financial "
        "pathway coverage or service eligibility. Defaults to false when "
        "these facts are not supplied."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67"
