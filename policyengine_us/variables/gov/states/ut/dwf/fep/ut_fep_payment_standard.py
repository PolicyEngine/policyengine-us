from policyengine_us.model_api import *


class ut_fep_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.fep.payment_standard
        size = spm_unit("spm_unit_size", period)
        size_capped = min_(size, p.max_unit_size)
        return p.amount[size_capped]
