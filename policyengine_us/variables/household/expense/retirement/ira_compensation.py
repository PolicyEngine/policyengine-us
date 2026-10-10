from policyengine_us.model_api import *


class ira_compensation(Variable):
    value_type = float
    entity = Person
    label = "Compensation for IRA contribution limits"
    unit = USD
    documentation = (
        "Taxable wages, taxable alimony, and net self-employment earnings "
        "less deductible self-employment taxes and self-employed retirement "
        "plan contributions. A net self-employment loss does not reduce wages."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#f_1",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(person, period, parameters):
        wages = person("irs_employment_income", period)
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
