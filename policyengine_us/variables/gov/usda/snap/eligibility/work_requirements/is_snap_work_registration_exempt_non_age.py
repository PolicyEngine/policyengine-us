from policyengine_us.model_api import *


class is_snap_work_registration_exempt_non_age(Variable):
    value_type = bool
    entity = Person
    label = "Person is exempt from SNAP work registration under non-age criteria"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_1",
        "https://www.law.cornell.edu/uscode/text/7/2015#d_2",
        "https://www.law.cornell.edu/cfr/text/7/273.24#c_2",
        "https://www.law.cornell.edu/uscode/text/7/2015#o_3",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.work_requirements.general
        # Age-based exemptions under (b)(1)(i) are handled in the
        # age-based work registration exemption logic.
        # (ii) Physically or mentally unfit for employment. 7 CFR
        # 273.7(b)(1)(ii) leaves the unfitness determination to the State
        # agency; 7 CFR 273.24(c)(2)(i) treats receipt of temporary or
        # permanent disability benefits as establishing unfitness, applied
        # here by analogy, so the USDA receipt-based definition also exempts.
        is_disabled = person("is_disabled", period) | person(
            "is_usda_disabled", period.this_year
        )
        # (iii) Subject to and complying with TANF work requirements.
        # TANF enrollment is an existing SPM-unit input; person-level
        # compliance is a documented input the data layer may not yet
        # populate (PolicyEngine/populace#248). We gate on enrollment
        # because a person cannot be subject to TANF work requirements
        # without receiving TANF.
        complying_with_tanf_work_requirements = person.spm_unit(
            "is_tanf_enrolled", period
        ) & person("is_complying_with_tanf_work_requirements", period)
        # (iv) Responsible for care of dependent child under 6
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)
        is_young_child = age < p.age_threshold.caring_dependent_child
        has_child_under_6 = person.spm_unit.any(is_dependent & is_young_child)
        # (iv) Responsible for care of incapacitated person
        has_incapacitated_person = person.spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        # (viii) Enrolled at least half-time in school/training/higher ed
        is_student = person("is_snap_higher_ed_student", period)
        # (v) Receiving unemployment compensation, or has applied for it
        # but not yet begun receiving it — 7 CFR 273.7(b)(1)(v). Receipt is
        # limited to the months allocated from weeks unemployed (all 12
        # months when weeks unemployed are not reported).
        receiving_ui = person("is_receiving_unemployment_compensation", period)
        applied_for_ui = person("has_applied_for_unemployment_compensation", period)
        # (vi) Regular participant in a drug addiction or alcoholic
        # treatment and rehabilitation program — 7 CFR 273.7(b)(1)(vi).
        in_treatment_program = person("is_in_substance_use_treatment_program", period)
        # (vii) Employed or self-employed and working at least 30 hours
        # weekly or earning at least the federal minimum wage times 30 hours.
        is_employed_exempt = person("is_snap_work_registration_exempt_employed", period)
        return (
            is_disabled
            | complying_with_tanf_work_requirements
            | has_child_under_6
            | has_incapacitated_person
            | is_student
            | receiving_ui
            | applied_for_ui
            | in_treatment_program
            | is_employed_exempt
        )
