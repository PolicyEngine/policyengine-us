from policyengine_us.model_api import *


class foreign_earned_income_exclusion_gross_person(Variable):
    value_type = float
    entity = Person
    label = "Own gross foreign earned income and housing exclusions"
    unit = USD
    documentation = (
        "The person's own exclusions under 26 U.S.C. 911(a): line 43 of the "
        "Form 2555 the person files (the line 36 housing exclusion plus the "
        "line 42 foreign earned income exclusion), before line 44 allocable "
        "deductions and without the line 50 housing deduction, which section "
        "911(c)(4) treats as a deduction, not an exclusion. It is "
        "foreign_earned_income_exclusion_gross_person_reported when that is "
        "zero or more. When it is negative (its default is -1), the head "
        "of a return with one head or spouse gets the return's line 43, "
        "foreign_earned_income_exclusion_gross (as entered, or lines 36 and 42 "
        "from the Form 2555 leaves). On a joint return the model can't tell "
        "which spouse earned the excluded income, so each spouse gets zero. "
        "The legacy foreign_earned_income_exclusion (worksheet line 2c: line "
        "43 less line 44, plus line 50, less line 2b) never stands in for "
        "line 43: no inputs can show that it equals line 43. Without Form "
        "2555 leaves nothing shows that lines 44 and 50 and worksheet line 2b "
        "are zero, and once any leaf is entered, even a zero, the leaves give "
        "line 43 as lines 36 and 42. A filer who knows line 43 enters it as "
        "foreign_earned_income_exclusion_gross_person_reported, which applies "
        "only to the year entered. Each person's value depends only on their "
        "own inputs and their own return's, apart from a batch that mixes an "
        "entered foreign_earned_income_exclusion_gross in one return with "
        "Form 2555 leaves in another, or enters a Form 2555 leaf for "
        "different years in different returns, where one return's entry for "
        "a later year stops another's earlier entry carrying into it; "
        "policyengine_us.Simulation rejects both. Supply "
        "foreign_earned_income_exclusion_gross_person_reported rather than "
        "setting this variable: an input here applies to every person in the "
        "simulation, and people without a value get zero. The tax unit "
        "amounts still drive federal tax."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/911#a",
        # Section 911(c)(4)(A): a housing cost amount not attributable to
        # employer provided amounts is a deduction (Form 2555 line 50).
        "https://www.law.cornell.edu/uscode/text/26/911#c_4",
        # Section 6012(c): gross income for the filing requirement is
        # computed without regard to the section 911 exclusion.
        "https://www.law.cornell.edu/uscode/text/26/6012#c",
        "https://www.irs.gov/pub/irs-prior/f2555--2025.pdf#page=3",
        # Married couples: each spouse figures the exclusion on a separate
        # Form 2555, and the joint return excludes the sum.
        "https://www.irs.gov/pub/irs-prior/i2555--2025.pdf#page=6",
    )

    def formula(person, period, parameters):
        reported = person(
            "foreign_earned_income_exclusion_gross_person_reported", period
        )
        # The return's Form 2555 line 43: foreign_earned_income_exclusion_gross
        # as entered, or the line 36 and line 42 leaves it adds.
        return_exclusion = max_(
            person.tax_unit("foreign_earned_income_exclusion_gross", period), 0
        )
        head = person("is_tax_unit_head", period)
        one_filer = person.tax_unit("head_spouse_count", period) == 1
        fallback = where(head & one_filer, return_exclusion, 0)
        # Any negative amount, such as the default -1, means not supplied:
        # line 43 adds two exclusions and can't be negative.
        return where(reported >= 0, reported, fallback)
