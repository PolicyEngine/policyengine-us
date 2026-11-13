from policyengine_us.model_api import *


class ia_ssa_rcf_shares_room_with_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SSA residential care resident shares a room with the spouse"
    definition_period = MONTH
    defined_for = StateCode.IA
    default_value = False
    documentation = "Both spouses occupy the same room of the residential care facility. Reporting this fact for either co-resident spouse applies it to both. Without prior SSI receipt, the entry-month couple budget requires this fact as well as entry by both spouses in that month."
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=1"
