from policyengine_us.model_api import *


class ct_tfa_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf?rev=f9c7a2028b6e409689d213d1966d6818&hash=9DDB6100DBC3D983F7946E33D702B2C8#page=53"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment
        size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(size, 8)

        return p.amount[capped_unit_size]
