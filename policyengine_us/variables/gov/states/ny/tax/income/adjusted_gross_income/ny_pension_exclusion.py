from policyengine_us.model_api import *


class ny_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "New York pension exclusion"
    unit = USD
    documentation = "Exclusion for pension income for eligible individuals."
    definition_period = YEAR
    dict(
        title="N.Y. Comp. Codes R. & Regs. tit. 20 § 112.3",
        href="https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-2-residents/part-112-new-york-adjusted-gross-income-of-a-resident-individual/section-1123-modifications-reducing-federal-adjusted-gross-income",  # (c)
    )

    def formula(person, period, parameters):
        pension_income = person("taxable_pension_income", period)
        age = person("age", period)

        # Fetching values from separate YAML files
        p = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion

        meets_age_test = age >= p.min_age

        return meets_age_test * min_(pension_income, p.cap)
