from policyengine_us.model_api import *


class ga_military_retirement_exclusion_person(Variable):
    value_type = float
    entity = Person
    label = "Georgia military retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",  # Page 16
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807",
    )
    defined_for = "ga_military_retirement_exclusion_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ga.tax.income.agi.exclusions.military_retirement
        earned_income = person("earned_income", period)
        additional_subtraction_eligible = (
            earned_income > p.additional.earned_income_threshold
        )
        military_retirement_income = person("military_retirement_pay", period)
        additional_amount = (
            additional_subtraction_eligible * p.additional.amount
        )
        uncapped_exclusion_amount = p.base + additional_amount
        return min_(uncapped_exclusion_amount, military_retirement_income)
