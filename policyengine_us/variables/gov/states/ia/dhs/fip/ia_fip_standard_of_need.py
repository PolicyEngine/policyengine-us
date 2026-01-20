from policyengine_us.model_api import *


class ia_fip_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP standard of need"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip
        people = spm_unit("spm_unit_size", period)
        capped_people = min_(people, p.max_unit_size).astype(int)
        additional_people = people - capped_people

        base = p.need_standard.main[capped_people]
        additional_amount = p.need_standard.additional * additional_people
        monthly = base + additional_amount
        return monthly * MONTHS_IN_YEAR
