from policyengine_us.model_api import *


class ia_fip_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP payment standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=31"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip
        people = spm_unit("spm_unit_size", period)
        capped_people = min_(people, p.max_unit_size).astype(int)
        additional_people = people - capped_people

        base = p.payment_standard.main[capped_people]
        additional_amount = p.payment_standard.additional * additional_people
        monthly = base + additional_amount
        return monthly * MONTHS_IN_YEAR
