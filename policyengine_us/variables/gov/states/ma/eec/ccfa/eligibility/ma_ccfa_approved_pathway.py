from policyengine_us.model_api import *


class ma_ccfa_approved_pathway(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts CCFA approved Pathway to Full-Time Employment"
    documentation = "An active, approved 12-month CCFA Pathway authorization for employment or employment plus education or training totaling at least 15 and less than 25 hours weekly. Not valid at the immediately following reauthorization. The caller must supply the verified authorization, including its end date and prior-use restriction."
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://archives.lib.state.ma.us/server/api/core/bitstreams/5c538ae6-69c2-43df-bf85-10d2f5e5bfc2/content#page=5"
