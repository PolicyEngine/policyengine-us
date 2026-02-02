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
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.oh.odjfs.owf.payment_standard

        # Use table lookup for groups up to max_size, increment for larger groups
        max_size = p.max_group_size
        table_size = min_(size, max_size)
        additional_person = max_(size - max_size, 0)
        additional_amount = additional_person * p.additional_person

        # Base 2017 amounts adjusted by cumulative Social Security COLA
        pre_cola_amount = p.amounts[table_size] + additional_amount

        return pre_cola_amount * p.cola_multiplier
