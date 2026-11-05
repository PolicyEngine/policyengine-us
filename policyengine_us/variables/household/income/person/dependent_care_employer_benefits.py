from policyengine_us.model_api import *


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
        "exclusion returns as taxable_dependent_care_benefits."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/129#a_1",
        "https://www.law.cornell.edu/uscode/text/26/3121#a_18",
        "https://www.law.cornell.edu/uscode/text/26/3306#b_13",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
    )
