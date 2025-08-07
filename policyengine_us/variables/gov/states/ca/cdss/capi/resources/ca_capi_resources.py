from policyengine_us.model_api import *


class ca_capi_resources(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "California CAPI resources"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    adds = ["ssi_countable_resources", "ca_capi_countable_vehicle_value"]
