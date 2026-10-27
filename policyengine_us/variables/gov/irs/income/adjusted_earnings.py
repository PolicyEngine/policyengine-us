from policyengine_us.model_api import *


class adjusted_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Personal earned income adjusted for self-employment tax"
    documentation = (
        "Earned income under IRC 32(c)(2): wages includible in gross income "
        "(after pre-tax payroll deductions such as traditional elective "
        "deferrals) plus self-employment earnings less the deductible part "
        "of self-employment tax. It sets each spouse's earned income limit "
        "for the child and dependent care credit and the dependent care "
        "assistance exclusion."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_2_A",
        "https://www.law.cornell.edu/uscode/text/26/21#d_1",
        "https://www.law.cornell.edu/cfr/text/26/1.21-2#b_3",
        "https://www.law.cornell.edu/uscode/text/26/129#e_2",
        "https://www.law.cornell.edu/uscode/text/26/402#e_3",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - p.self_emp_tax_adj)
            * p.employer_share
            * person("self_employment_tax", period)
        )
        # IRC 32(c)(2)(A)(i) counts employee compensation "only if such
        # amounts are includible in gross income", and Treas. Reg.
        # 1.21-2(b)(3) and IRC 129(e)(2) use that definition. Form 2441
        # (lines 4, 5, 18 and 19) starts from Form 1040 line 1z, which
        # leaves out pre-tax payroll deductions such as traditional
        # elective deferrals (IRC 402(e)(3)). Gross earned_income is kept
        # for programs that count wages before these deductions.
        excluded_wages = person("employment_income", period) - person(
            "irs_employment_income", period
        )
        # Disability pay reported as wages is earned income (Pub. 503 (2024),
        # file page 4).
        earnings = add(person, period, ["earned_income", "earned_disability_benefits"])
        return max_(0, earnings - excluded_wages - adjustment)
