from policyengine_us.model_api import *


class fl_oss_income_standard(Variable):
    value_type = float
    entity = Person
    label = "Florida OSS income standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.oss
        track = person("fl_oss_program_track", period)
        is_redesign = track == track.possible_values.REDESIGN
        provider_rate = person("fl_oss_provider_rate", period)
        # Redesign: income standard = provider rate + PNA offset
        # Protected: income standard = provider rate
        pna_offset = where(
            is_redesign,
            p.redesign.income_standard_pna_offset,
            0,
        )
        return provider_rate + pna_offset
