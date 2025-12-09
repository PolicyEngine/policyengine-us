from policyengine_us.model_api import *


class mn_mfip_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Transitional Standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.house.mn.gov/hrd/pubs/ss/ssmfip.pdf#page=5"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.mfip.payment_standard
        size = spm_unit("spm_unit_size", period)
        capped_size = min_(size, p.max_unit_size)
        base_amount = p.amount[capped_size]
        additional_persons = max_(size - p.max_unit_size, 0)
        return base_amount + additional_persons * p.additional_person_increment
