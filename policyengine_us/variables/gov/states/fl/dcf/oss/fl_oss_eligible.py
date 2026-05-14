from policyengine_us.model_api import *


# Implicit SSI living-arrangement invariant: an OSS-eligible person is
# always OWN_HOUSEHOLD in ssi_federal_living_arrangement. None of the
# three reduction triggers fires for a legitimate ALF/AFCH/MHRTF
# resident: MEDICAL_TREATMENT_FACILITY requires Medicaid paying >50%
# (OSS exists because it is not); CHILD_IN_PARENTAL_HOUSEHOLD requires
# under-18 (OSS requires aged/blind/disabled); ANOTHER_PERSONS_HOUSEHOLD
# requires free shelter and meals from a private household (OSS
# residents pay the provider). FAC 65A-2 gates eligibility on facility
# type, not on SSI code, so this formula does not cross-check against
# ssi_federal_living_arrangement; inconsistent inputs (e.g. setting
# both fl_oss_community_care_type = ALF and
# ssi_lives_in_medical_treatment_facility = True) will produce
# nonsensical results.
class fl_oss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Florida OSS eligible"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.flrules.org/gateway/RuleNo.asp?title=PUBLIC%20ASSISTANCE&ID=65A-2.032",
        "https://www.flrules.org/gateway/RuleNo.asp?title=PUBLIC%20ASSISTANCE&ID=65A-2.033",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.oss
        categorically_eligible = person("is_ssi_eligible", period)
        living_arrangement = person("fl_oss_living_arrangement", period)
        LA = living_arrangement.possible_values
        in_facility = living_arrangement != LA.NONE
        program_track = person("fl_oss_program_track", period)
        has_track = program_track != program_track.possible_values.NONE
        is_protected = program_track == program_track.possible_values.PROTECTED
        track_valid = where(is_protected, p.protected.in_effect, has_track)
        # FAC 65A-2.033(1): "receiving SSI checks" (Group 1).
        receives_ssi = person("ssi", period) > 0
        # FAC 65A-2.033(2): income within OSS income standard (Group 2).
        income_standard = person("fl_oss_income_standard", period)
        countable_income = person("ssi_countable_income", period)
        income_within_standard = countable_income <= income_standard
        return (
            categorically_eligible
            & in_facility
            & track_valid
            & (receives_ssi | income_within_standard)
        )
