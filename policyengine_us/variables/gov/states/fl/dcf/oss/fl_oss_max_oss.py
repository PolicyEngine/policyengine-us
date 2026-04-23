from policyengine_us.model_api import *


class fl_oss_max_oss(Variable):
    value_type = float
    entity = Person
    label = "Florida OSS maximum payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.oss
        track = person("fl_oss_program_track", period)
        is_redesign = track == track.possible_values.REDESIGN
        couple_rate_applies = person("fl_oss_couple_rate_applies", period)
        if p.protected.in_effect:
            individual_cap = where(
                is_redesign,
                p.redesign.max_oss.individual,
                p.protected.max_oss.individual,
            )
            couple_cap = where(
                is_redesign,
                p.redesign.max_oss.couple,
                p.protected.max_oss.couple,
            )
        else:
            individual_cap = p.redesign.max_oss.individual
            couple_cap = p.redesign.max_oss.couple
        return where(couple_rate_applies, couple_cap / 2, individual_cap)
