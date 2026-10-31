from policyengine_us.model_api import *


class ca_capi(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "California CAPI"
    definition_period = YEAR
    defined_for = "ca_capi_eligible"
    reference = (
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=47"
    )

    adds = ["ca_capi_person"]
