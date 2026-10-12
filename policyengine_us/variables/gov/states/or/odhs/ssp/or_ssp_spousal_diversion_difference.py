from policyengine_us.model_api import *


class or_ssp_spousal_diversion_difference(Variable):
    value_type = float
    entity = Person
    label = "Oregon additional diversion available under nursing facility placement"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0700.pdf",
    )
    documentation = "State-calculated excess of permitted nursing-facility diversion over community-care diversion, using 461-160-0620 liability rules. Requires an approved request under 461-155-0700(1)(d)."
