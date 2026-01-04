from policyengine_us.model_api import *


class ct_tfa_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=53"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment
        size = spm_unit("spm_unit_size", period.this_year)
        capped_unit_size = min_(size, p.max_unit_size)

        return p.amount[capped_unit_size]
