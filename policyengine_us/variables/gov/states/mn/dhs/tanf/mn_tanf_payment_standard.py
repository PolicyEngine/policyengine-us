from policyengine_us.model_api import *


class mn_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP Transitional Standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.mn.dhs.tanf.payment_standard
        capped_unit_size = min_(unit_size, p.max_unit_size)
        return p.amount[capped_unit_size]
