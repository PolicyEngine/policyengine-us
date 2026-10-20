from policyengine_us.model_api import *


class standard_deduction_worksheet_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = (
        "Earned income for the standard deduction worksheet for dependents, by person"
    )
    unit = USD
    documentation = (
        "A person's earned income on the Standard Deduction Worksheet for "
        "Dependents: wages from Form W-2 box 1, which leave out elective "
        "deferrals, plus disability pensions reported as wages before minimum "
        "retirement age and business and farm income, minus the deductible part "
        "of their self-employment tax. Not floored at zero, so that on a "
        "joint return one spouse's loss offsets the other's earnings."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        # Form 1040 instructions. Line 1a is the total of Form(s) W-2, box 1
        # (PDF page 23). An elective deferral "isn't included as income in
        # box 1 of your Form W-2" (page 25). Worksheet footnote: "Generally,
        # your earned income is the total of the amount(s) you reported on
        # Form 1040 or 1040-SR, line 1z, and Schedule 1, lines 3, 6, 8r, 8t,
        # and 8u minus the amount, if any, on Schedule 1, line 15" (page 34
        # in 2024, page 35 in 2025).
        # PDF pages 23, 25, 34
        "https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf#page=23",
        # PDF pages 23, 25, 35
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=23",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.filing_requirement.dependent
        # Form 1040 line 1z wages (irs_employment_income, after elective
        # deferrals and other pretax payroll deductions) and Schedule 1 lines
        # 3 and 6. A business or farm loss reduces the total.
        earned_income = add(person, period, p.earned_income_sources)
        # Form 1040 line 1h disability pensions are part of line 1z, but
        # are modeled separately from irs_employment_income.
        earned_income += person("earned_disability_benefits", period)
        # Schedule 1, line 15: the deductible part of self-employment tax.
        return earned_income - person("self_employment_tax_ald_person", period)
