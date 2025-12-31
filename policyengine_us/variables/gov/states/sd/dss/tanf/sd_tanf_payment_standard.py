from policyengine_us.model_api import *


class sd_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Dakota TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-05-03"
    )
    defined_for = StateCode.SD

    def formula(spm_unit, period, parameters):
        family_size = spm_unit.nb_persons()
        p = parameters(period).gov.states.sd.dss.tanf.payment_standard
        is_shared = spm_unit("sd_tanf_is_shared_living", period)

        max_table_size = p.max_table_size
        base_size = min_(family_size, max_table_size)
        independent_amount = p.independent_living.calc(base_size)
        shared_amount = p.shared_living.calc(base_size)

        extra_persons = max_(family_size - max_table_size, 0)
        increment = p.additional_person_increment * extra_persons

        base_amount = where(is_shared, shared_amount, independent_amount)
        return base_amount + increment
