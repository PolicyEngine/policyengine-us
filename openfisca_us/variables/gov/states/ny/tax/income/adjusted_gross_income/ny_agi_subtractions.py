from openfisca_us.model_api import *


class ny_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY AGI subtractions"
    unit = USD
    documentation = "Subtractions from NY AGI over federal AGI."
    definition_period = YEAR
    dict(
        title="N.Y. Comp. Codes R. & Regs. tit. 20 § 112.3",
        href="https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-2-residents/part-112-new-york-adjusted-gross-income-of-a-resident-individual/section-1123-modifications-reducing-federal-adjusted-gross-income",
    )

    def formula(tax_unit, period, parameters):
        taxable_ss = add(tax_unit, period, ["taxable_social_security"])
        us_govt_interest = tax_unit("us_govt_interest", period)
        investment_in_529_plan = tax_unit("investment_in_529_plan", period)
        person = tax_unit.members
        pension_income = person("pension_income", period)
        age = person("age", period)

        pension_exclusion = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion
        meets_age_test = age >= pension_exclusion.min_age
        deductible_pensions = meets_age_test * min_(
            pension_income, pension_exclusion.cap
        )

        return (
            taxable_ss
            + us_govt_interest
            + investment_in_529_plan
            + tax_unit.sum(deductible_pensions)
        )
