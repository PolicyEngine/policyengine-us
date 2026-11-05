from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.retirement._ira_supplied_contributions import (
    _is_supplied,
)


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
        # tests/test_ira_formula_differential.py runs this body on its own,
        # so it repeats the sum in ira_compensation_without_line_1e and
        # adds line 1e.
        # Disability pay treated as wages before minimum retirement age is
        # compensation (Pub. 4491 (Rev. 10-2025), file page 144). Taxable
        # dependent care benefits (Form 1040 line 1e) are includible pay for
        # services (Treas. Reg. 1.219-1(c)(1)).
        wages = add(
            person,
            period,
            [
                "irs_employment_income",
                "earned_disability_benefits",
                "taxable_dependent_care_benefits",
            ],
        )
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


def ira_compensation_without_line_1e(person, period):
    """IRC 219(f)(1) compensation without Form 1040 line 1e.

    The ira_compensation formula repeats this sum and adds line 1e.
    """
    # Disability pay treated as wages before minimum retirement age is
    # compensation (Pub. 4491 (Rev. 10-2025), file page 144).
    wages = add(person, period, ["irs_employment_income", "earned_disability_benefits"])
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


def dependent_ira_compensation(person, period):
    """IRA compensation for a tax unit dependent's own return.

    A supplied ira_compensation is used as given. Otherwise this leaves out
    the dependent's own line 1e, which would need the filer's filing status.
    """
    if _is_supplied(person.simulation, "ira_compensation", period):
        return person("ira_compensation", period)
    return ira_compensation_without_line_1e(person, period)
