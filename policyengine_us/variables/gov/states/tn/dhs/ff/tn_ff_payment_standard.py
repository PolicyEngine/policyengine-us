from policyengine_us.model_api import *


class tn_ff_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # NOTE: Tennessee has a Differential Grant Payment Amount (DGPA) for
        # caretakers who are age 60+, disabled, or provide care for disabled.
        # This is not currently modeled; we only return the Standard Payment
        # Amount (SPA). DGPA parameters exist for future implementation.
        p = parameters(period).gov.states.tn.dhs.ff.payment
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_family_size)

        return p.standard_payment_amount[capped_size]
