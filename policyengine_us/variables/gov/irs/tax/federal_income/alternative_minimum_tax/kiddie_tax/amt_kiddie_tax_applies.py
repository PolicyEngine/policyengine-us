from policyengine_us.model_api import *


class amt_kiddie_tax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax kiddie tax applies"
    documentation = "Whether the kiddie tax applies to the tax unit"
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/1#g_2_A",
        "https://www.irs.gov/publications/p929",
    ]

    def formula(tax_unit, period, parameters):
        # The kiddie tax applies to children under 19, or under 24 if a
        # full-time student. Per IRC 1(g)(2)(A), the age requirements
        # reference Section 152(c)(3), same as the dependent definition.
        p = parameters(period).gov.irs.dependent.ineligible_age

        # Get student status from person-level data
        person = tax_unit.members
        is_student = person("is_full_time_student", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        # Check if head or spouse is a full-time student
        head_is_student = tax_unit.any(is_student & is_head)
        spouse_is_student = tax_unit.any(is_student & is_spouse)

        # Get tax unit level ages
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        # Determine age limits based on student status
        head_age_limit = where(head_is_student, p.student, p.non_student)
        spouse_age_limit = where(spouse_is_student, p.student, p.non_student)

        # Check head age: head must be young (and exist - age != 0)
        young_head = (age_head != 0) & (age_head < head_age_limit)

        # Check spouse age: spouse must be young (or not exist - age == 0)
        no_or_young_spouse = (age_spouse == 0) | (
            age_spouse < spouse_age_limit
        )

        return young_head & no_or_young_spouse
