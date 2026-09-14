from policyengine_us.model_api import *


class ma_ccfa_approved_parental_leave(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts CCFA approved parental leave"
    documentation = "An active CCFA-approved temporary leave from employment, education or training for birth, placement or care of a child. Limited to one parent in the family and the authorized 12-month period."
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://archives.lib.state.ma.us/server/api/core/bitstreams/5c538ae6-69c2-43df-bf85-10d2f5e5bfc2/content#page=6"
