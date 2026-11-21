from policyengine_us.model_api import *


def form_2441_line_15(person, period, parameters, always_count_line_13=False):
    """Each person's part of Form 2441 line 15 (FTB 3506 line 16).

    Line 12 is dependent_care_employer_benefits: W-2 box 10 benefits, not
    counting any box 10 amount above the plan's exclusion, which the employer
    already reports as box 1 wages. Line 15 adds prior-year benefits used in
    this year's grace period (line 13) and subtracts amounts forfeited or
    carried forward to the next year (line 14). Line 14 amounts come from
    line 12 (on the 2021-2024 forms, line 12 or 13), and each person's come
    from their own benefits, so the result is floored at zero for each
    person. A negative line 13 or line 14 entry counts as zero.

    For 2021 and 2022, Form 2441 line 21 adds line 13 to the cap, and
    temporary relief rules govern carryovers from plan years ending in 2020
    and 2021. The model doesn't apply those rules, so in those years the
    federal calculation leaves line 13 out of line 15, as it does out of the
    cap (prior_year_carryover_omitted). Alabama's 2021 recompute pins that
    parameter to its 2020 value, false, so it counts line 13, as the 2020
    form does. FTB 3506 line 22 never adds line 13 to California's cap, and
    FTB 3506 line 14 enters the Form 2441 line 13 amount, so California
    passes always_count_line_13 and counts it in every year.
    """
    line_12 = person("dependent_care_employer_benefits", period)
    line_13 = max_(
        person("dependent_care_employer_benefits_prior_year_carryover", period), 0
    )
    line_14 = max_(
        person(
            "dependent_care_employer_benefits_forfeited_or_carried_forward",
            period,
        ),
        0,
    )
    # Only a carryover needs the relief-year switch, so a return without one
    # never reads it, as in years before the parameter's first value.
    if not always_count_line_13 and np.any(line_13 > 0):
        p = parameters(period).gov.irs.gross_income.dependent_care_assistance_programs
        line_13 = where(p.prior_year_carryover_omitted, 0, line_13)
    return max_(line_12 + line_13 - line_14, 0)


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
