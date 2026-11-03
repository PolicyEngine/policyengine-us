from policyengine_us.model_api import *


class ira_compensation(Variable):
    value_type = float
    entity = Person
    label = "Compensation for IRA contribution limits"
    unit = USD
    documentation = (
        "Taxable wages, including taxable dependent care benefits (Form 1040 "
        "line 1e), taxable alimony, and net self-employment earnings "
        "less deductible self-employment taxes and self-employed retirement "
        "plan contributions. A net self-employment loss does not reduce wages."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#f_1",
        "https://www.ecfr.gov/current/title-26/section-1.219-1",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2",
        "https://www.irs.gov/publications/p590a",
        "https://www.irs.gov/pub/irs-pdf/p4491.pdf#page=144",
    )

    def formula(person, period, parameters):
        return ira_compensation_amount(person, period, include_line_1e=True)


def ira_compensation_amount(person, period, include_line_1e):
    """IRC 219(f)(1) compensation, with or without Form 1040 line 1e.

    Treas. Reg. 1.219-1(c)(1) counts pay for personal services that is
    includible in gross income, so taxable dependent care benefits (Form
    2441 line 26, Form 1040 line 1e) are compensation.
    """
    # Disability pay treated as wages before minimum retirement age is
    # compensation (Pub. 4491 (Rev. 10-2025), file page 144).
    wage_sources = ["irs_employment_income", "earned_disability_benefits"]
    if include_line_1e:
        wage_sources.append("taxable_dependent_care_benefits")
    wages = add(person, period, wage_sources)
    alimony = person("taxable_alimony_income", period)
    self_employment_earnings = (
        add(
            person,
            period,
            [
                "self_employment_income",
                "sstb_self_employment_income",
                "farm_operations_income",
                "partnership_self_employment_net_earnings",
            ],
        )
        - person("self_employment_tax_ald_person", period)
        - person("self_employed_pension_contribution_ald_person", period)
    )
    return max_(wages, 0) + max_(alimony, 0) + max_(self_employment_earnings, 0)
