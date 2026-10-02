from policyengine_us.model_api import *


class ny_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "New York pension exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-2-residents/part-112-new-york-adjusted-gross-income-of-a-resident-individual/section-1123-modifications-reducing-federal-adjusted-gross-income",
        # N.Y. Tax Law § 612(c)(3-a)
        "https://newyork.public.law/laws/n.y._tax_law_section_612",
        # 2025 Form IT-201-I, line 29 and "Married taxpayers"
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=9",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=10",
    )

    def formula(person, period, parameters):
        # Fetching values from separate YAML files
        p = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion

        pension_income = add(person, period, p.sources)
        age = person("age", period)
        meets_age_test = age >= p.min_age
        # The exclusion applies only to pensions included in federal AGI.
        # Dependents' pensions are not; they report them on their own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return head_or_spouse * meets_age_test * min_(pension_income, p.cap)
