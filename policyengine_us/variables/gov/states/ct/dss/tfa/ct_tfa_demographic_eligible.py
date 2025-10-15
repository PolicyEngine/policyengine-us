"""
Connecticut TFA demographic eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_demographic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA demographic eligibility"
    definition_period = YEAR
    defined_for = StateCode.CT
    documentation = (
        "Connecticut TFA demographic eligibility requires families with dependent "
        "children under age 18 (or age 18 if enrolled full-time in high school or "
        "vocational school), and pregnant women may also qualify. Children must "
        "live with a related adult or an adult who has filed for guardianship."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Eligibility Criteria; "
        "Connecticut TFA Fact Sheet - Household Composition; "
        "https://portal.ct.gov/dss/knowledge-base/articles/fact-sheets-and-brochures-articles/fact-sheets-articles/tfa-fact-sheet"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa
        person = spm_unit.members

        # Check for dependent children
        age = person("age", period)
        is_student = person("is_full_time_student", period)
        max_age = p.age_limits.max_age

        # Dependent child if under 18, or age 18 and full-time student
        is_dependent_child = (age < max_age) | ((age == max_age) & is_student)

        has_dependent_child = spm_unit.any(is_dependent_child)

        # Check for pregnant women
        is_pregnant = person("is_pregnant", period)
        has_pregnant_member = spm_unit.any(is_pregnant)

        # Eligible if has dependent child or pregnant member
        return has_dependent_child | has_pregnant_member
