from policyengine_us.model_api import *


class ga_retirement_income_exclusion_retirement_income(Variable):
    value_type = float
    entity = Person
    label = "Georgia retirement income for the retirement income exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download",  # Page 15
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",  # Page 15
        "https://dor.georgia.gov/document/document/2024-it-511-individual-income-tax-booklet/download",  # Schedule 1, Page 2
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807",
    )
    defined_for = StateCode.GA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions.retirement
        # Georgia Schedule 1 Page 2 floors the earned-income portion and the
        # remaining retirement-income sources separately before adding them.
        countable_earned_income = max_(
            0, person("ga_retirement_exclusion_countable_earned_income", period)
        )
        other_retirement_income = add(person, period, p.sources)
        countable_other_retirement_income = max_(0, other_retirement_income)
        return countable_earned_income + countable_other_retirement_income
