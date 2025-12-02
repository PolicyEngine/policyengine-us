from policyengine_us.model_api import *


class oh_owf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio OWF payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://emanuals.jfs.ohio.gov/CashFoodAssist/CAM/ACT/"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.oh.odjfs.owf.payment_standard

        # For assistance groups up to max_group_size, use table lookup
        # For groups larger than max_group_size, calculate using increment
        max_size = p.max_group_size
        table_size = min_(size, max_size)
        extra_members = max_(size - max_size, 0)

        base_amount = p.amounts[table_size]
        additional_amount = extra_members * p.additional_person_increment

        return base_amount + additional_amount
