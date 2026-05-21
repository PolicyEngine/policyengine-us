from policyengine_us.model_api import *


class az_ccap_quality_enhanced_provider(Variable):
    value_type = bool
    entity = Person
    label = "Arizona Child Care Assistance Program quality enhanced provider"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/des-contracted-child-care-provider-resources",
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf#page=1",
    )
