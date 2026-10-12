from policyengine_us.model_api import *


class mt_ssp_in_state_custody(Variable):
    value_type = bool
    entity = Person
    label = "Retained in Montana legal custody while living outside Montana"
    definition_period = MONTH
    default_value = False
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN"
    documentation = "Montana retains legal custody and responsibility for the certified SSI placement."
