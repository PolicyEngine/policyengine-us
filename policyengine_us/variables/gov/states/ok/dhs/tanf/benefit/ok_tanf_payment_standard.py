from policyengine_us.model_api import *


class ok_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-59"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf.benefit
        unit_size = spm_unit("spm_unit_size", period)
        return p.payment_standard.calc(unit_size)
