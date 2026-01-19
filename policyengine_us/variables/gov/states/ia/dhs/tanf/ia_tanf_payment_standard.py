from policyengine_us.model_api import *


class ia_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF payment standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        capped_people = min_(people, 10).astype(int)
        additional_people = people - capped_people
        p = parameters(period).gov.states.ia.dhs.tanf.payment_standard
        base = p.main[capped_people]
        additional_amount = p.additional * additional_people
        monthly = base + additional_amount
        return monthly * MONTHS_IN_YEAR
