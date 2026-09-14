from policyengine_us.model_api import *


class ma_ccfa_approved_domestic_violence(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts CCFA approved domestic violence service need"
    documentation = "An active, documented CCFA domestic violence service need approved by the subsidy administrator."
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://archives.lib.state.ma.us/server/api/core/bitstreams/5c538ae6-69c2-43df-bf85-10d2f5e5bfc2/content#page=6"
