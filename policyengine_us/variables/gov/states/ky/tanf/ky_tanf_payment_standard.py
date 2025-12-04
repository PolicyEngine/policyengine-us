from policyengine_us.model_api import *


class ky_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky Transitional Assistance Program payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.tanf
        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)
        return p.payment_standard[capped_size]
