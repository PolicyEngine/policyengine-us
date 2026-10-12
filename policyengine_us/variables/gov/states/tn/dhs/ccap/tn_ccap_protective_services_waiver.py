from policyengine_us.model_api import *


class tn_ccap_protective_services_waiver(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee CCAP protective services eligibility waiver"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=28",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=32",
    )
