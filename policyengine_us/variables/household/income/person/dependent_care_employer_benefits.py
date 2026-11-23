from policyengine_us.model_api import *


def form_2441_line_15(person, period):
    """Each person's part of Form 2441 line 15 (FTB 3506 line 16).

    Line 12 is dependent_care_employer_benefits: W-2 box 10 benefits, not
    counting any box 10 amount above the plan's exclusion, which the employer
    already reports as box 1 wages. Line 15 subtracts the amounts forfeited
    or carried forward to the next year (line 14). Line 13, prior-year
    benefits used this year (in the grace period; in 2021 and 2022, also
    carryovers under the relief rules), is not modeled and counts as zero;
    taxable_dependent_care_benefits_reported takes a line 26 amount for
    returns that have one. Each person's line 14 comes from their own line
    12, so the result is floored at zero for each person: a line 14 entry
    above the person's own line 12 reduces nothing else, and a negative line
    12 or line 14 entry counts as zero.
    """
    line_12 = person("dependent_care_employer_benefits", period)
    line_14 = max_(
        person(
            "dependent_care_employer_benefits_forfeited_or_carried_forward",
            period,
        ),
        0,
    )
    return max_(line_12 - line_14, 0)


class dependent_care_employer_benefits(Variable):
    value_type = float
    entity = Person
    label = "Dependent care benefits received from an employer"
    documentation = (
        "Dependent care assistance received as an employee (W-2 box 10, Form "
        "2441 line 12), not counting box 10 amounts the employer already "
        "reported as box 1 wages. Treated as a pre-tax payroll deduction "
        "included in employment_income, like a dependent care flexible "
        "spending account salary reduction: it is subtracted from income tax "
        "wages (irs_employment_income) and from FICA and FUTA wages "
        "(payroll_tax_gross_wages), and any part above the filer's IRC 129 "
        "exclusion returns as taxable_dependent_care_benefits. Report "
        "amounts later forfeited or carried forward here too, as box 10 "
        "does, and also in "
        "dependent_care_employer_benefits_forfeited_or_carried_forward "
        "(Form 2441 line 14)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/129#a_1",
        "https://www.law.cornell.edu/uscode/text/26/3121#a_18",
        "https://www.law.cornell.edu/uscode/text/26/3306#b_13",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
    )
