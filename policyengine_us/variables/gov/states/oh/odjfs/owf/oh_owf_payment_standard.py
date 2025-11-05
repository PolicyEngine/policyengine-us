from policyengine_us.model_api import *


class oh_owf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio OWF payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5107.04"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.oh.odjfs.owf.payment_standard

        # For assistance groups up to 8, use table lookup
        # For groups larger than 8, calculate using increment
        table_size = min_(size, 8)
        extra_members = max_(size - 8, 0)

        base_amount = p.amounts[table_size]
        additional_amount = extra_members * p.additional_person_increment

        return base_amount + additional_amount
