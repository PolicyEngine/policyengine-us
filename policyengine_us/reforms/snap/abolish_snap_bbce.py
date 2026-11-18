from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_abolish_snap_bbce() -> Reform:
    class meets_snap_categorical_eligibility(Variable):
        value_type = bool
        entity = SPMUnit
        label = "SNAP categorical eligibility"
        documentation = (
            "Whether this SPM unit is eligible for SNAP benefits via participation "
            "in other programs. While gov.contrib.snap.abolish_bbce.in_effect is "
            "true, eligibility for a non-cash TANF benefit (broad-based categorical "
            "eligibility) no longer qualifies the unit, following the removal of "
            "7 CFR 273.2(j)(2)(i)(B)-(C), (ii) and (iii) in USDA's proposed rule "
            "(91 FR 72454). SSI receipt by all members and TANF cash receipt keep "
            "qualifying the unit as in the baseline. The proposed rule's test that "
            "every member receives TANF assistance or SSI, and its general "
            "assistance routes, are not modeled."
        )
        definition_period = MONTH
        reference = (
            "https://www.govinfo.gov/content/pkg/USCODE-2019-title7/html/USCODE-2019-title7-chap51-sec2014.htm",
            "https://www.govinfo.gov/content/pkg/FR-2026-11-10/pdf/2026-22936.pdf#page=11",
        )

        def formula(spm_unit, period, parameters):
            p = parameters(period).gov
            programs = p.usda.snap.categorical_eligibility
            # The switch is read for each month, so the baseline list applies
            # in every period before the reform takes effect.
            if p.contrib.snap.abolish_bbce.in_effect:
                # Proposed 7 CFR 273.2(j)(2)(i)-(iii) keeps only the cash
                # assistance and SSI routes.
                programs = [
                    program
                    for program in programs
                    if program != "is_tanf_non_cash_eligible"
                ]
            spm_level_programs = [program for program in programs if program != "ssi"]
            person = spm_unit.members
            receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
            all_members_receive_ssi = spm_unit.all(receives_ssi)
            return (
                all_members_receive_ssi
                | (add(spm_unit, period, spm_level_programs) > 0)
                | spm_unit("receives_tanf", period)
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(meets_snap_categorical_eligibility)

    return reform


def create_abolish_snap_bbce_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_abolish_snap_bbce()

    p = parameters.gov.contrib.snap.abolish_bbce

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_abolish_snap_bbce()
    else:
        return None


abolish_snap_bbce = create_abolish_snap_bbce_reform(None, None, bypass=True)
