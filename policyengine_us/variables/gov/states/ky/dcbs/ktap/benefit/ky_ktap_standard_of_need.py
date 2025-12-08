from policyengine_us.model_api import *


class ky_ktap_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP standard of need"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.benefit
        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)
        return p.standard_of_need[capped_size]
