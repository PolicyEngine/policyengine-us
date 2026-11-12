from policyengine_us.model_api import *


class ia_ssa_rcf_received_ssi_before_entry(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA residential care resident received SSI before entry"
    definition_period = MONTH
    defined_for = StateCode.IA
    default_value = False
    documentation = "Receipt of SSI before the residential-care entry recorded in this month, rather than an individual SSI award after the spouses separate. Receipt by either spouse establishes the prior-SSI entry condition for the couple."
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=60"
