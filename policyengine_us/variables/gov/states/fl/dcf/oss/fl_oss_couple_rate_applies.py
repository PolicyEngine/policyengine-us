from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class fl_oss_couple_rate_applies(Variable):
    value_type = bool
    entity = Person
    label = "Florida OSS couple rate applies"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = "https://web.archive.org/web/20251030232040/https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf"

    def formula(person, period, parameters):
        # Requires: both spouses are an SSI eligible couple
        # (ssi_claim_is_joint handles Title XIX separation per
        # 20 CFR 416.1149 — see #8003), both pass SSI categorical
        # eligibility (resources + immigration), both reside in
        # a qualifying OSS facility, and both are on the same
        # non-NONE program track. Appendix A-12 defines couple
        # rates separately per track (Redesign vs Protected); a
        # couple with mismatched or missing tracks has no valid
        # couple rate.
        joint_claim = person("ssi_claim_is_joint", period)
        both_ssi_eligible = (
            _ssi_couple_total(
                person, period.this_year, person("is_ssi_eligible", period).astype(int)
            )
            == 2
        )
        living_arrangement = person("fl_oss_living_arrangement", period)
        in_facility = living_arrangement != living_arrangement.possible_values.NONE
        both_in_facility = (
            _ssi_couple_total(person, period.this_year, in_facility.astype(int)) == 2
        )
        program_track = person("fl_oss_program_track", period)
        TRACK = program_track.possible_values
        both_on_redesign = (
            _ssi_couple_total(
                person, period.this_year, (program_track == TRACK.REDESIGN).astype(int)
            )
            == 2
        )
        both_on_protected = (
            _ssi_couple_total(
                person, period.this_year, (program_track == TRACK.PROTECTED).astype(int)
            )
            == 2
        )
        both_on_same_track = both_on_redesign | both_on_protected
        return joint_claim & both_ssi_eligible & both_in_facility & both_on_same_track
