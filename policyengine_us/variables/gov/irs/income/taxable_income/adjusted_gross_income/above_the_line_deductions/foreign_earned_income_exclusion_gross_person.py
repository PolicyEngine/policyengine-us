from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import section_911_gross_exclusion


class foreign_earned_income_exclusion_gross_person(Variable):
    value_type = float
    entity = Person
    label = "Own gross foreign earned income and housing exclusions"
    unit = USD
    documentation = (
        "The person's own exclusions under 26 U.S.C. 911(a): line 43 of the "
        "Form 2555 the person files, before line 44 allocable deductions and "
        "without the line 50 housing deduction. Each spouse who claims the "
        "exclusion files a separate Form 2555. On a return with one head or "
        "spouse, this defaults to the return's gross section 911 exclusion "
        "(the amount tax_unit_is_required_to_file adds back under section "
        "6012(c)), credited to the head. On a joint return the model can't "
        "tell which spouse earned the excluded income, so this defaults to "
        "zero; enter each spouse's own line 43. The tax unit amounts "
        "(foreign_earned_income_exclusion_gross and its leaves) still drive "
        "federal tax."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        # Section 6012(c): gross income for the filing requirement is
        # computed without regard to the section 911 exclusion.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Married couples: each spouse figures the exclusion on a separate
        # Form 2555, and the joint return excludes the sum.
        "https://www.irs.gov/pub/irs-prior/i2555--2025.pdf#page=6",
    )

    def formula(person, period, parameters):
        return_exclusion = section_911_gross_exclusion(person.tax_unit, period)
        head = person("is_tax_unit_head", period)
        one_filer = person.tax_unit("head_spouse_count", period) == 1
        return where(head & one_filer, return_exclusion, 0)
