from policyengine_us.model_api import *


class fl_oss_provider_rate(Variable):
    value_type = float
    entity = Person
    label = "Florida OSS provider rate"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.oss
        track = person("fl_oss_program_track", period)
        is_redesign = track == track.possible_values.REDESIGN
        fbr_individual = parameters(period).gov.ssa.ssi.amount.individual
        if p.protected.in_effect:
            offset = where(
                is_redesign,
                p.redesign.provider_rate_offset,
                p.protected.provider_rate_offset,
            )
        else:
            offset = p.redesign.provider_rate_offset
        individual_rate = fbr_individual + offset
        couple_rate_applies = person("fl_oss_couple_rate_applies", period)
        couple_rate = 2 * individual_rate - p.couple_provider_rate_reduction
        return where(couple_rate_applies, couple_rate / 2, individual_rate)
