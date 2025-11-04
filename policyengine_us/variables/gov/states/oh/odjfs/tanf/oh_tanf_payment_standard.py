from policyengine_us.model_api import *


class oh_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio TANF payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5107.04"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.oh.odjfs.tanf.payment_standard

        # Get maximum size defined in parameter table
        max_size = p.max_size_in_table

        # For assistance groups up to max_size, use table lookup
        # For groups larger than max_size, calculate using increment
        table_size = min_(size, max_size)
        extra_members = max_(size - max_size, 0)

        base_amount = p.amounts[table_size]
        additional_amount = extra_members * p.additional_person_increment

        return base_amount + additional_amount
