from policyengine_us.model_api import *


class ga_military_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia military retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download"
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions.military
        military_age = person("age", period) < p.main.age
        military_additional_age = (
            person("age", period) < p.additional.threshold.age
        )
        military_income = person("military_retirement_pay", period)
        earned_income = person("earned_income", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)

        ## head military exclusion
        head_base = where(head & military_age, p.main.amount, 0)
        head_additional = where(
            head
            & military_additional_age
            & (earned_income > p.additional.threshold.income),
            p.additional.amount,
            0,
        )
        head_military_exclusion = tax_unit.sum(
            min_((head_base + head_additional), military_income)
        )

        ## spouse military exclusion
        spouse = person("is_tax_unit_spouse", period)
        spouse_base = where(spouse & military_age, p.main.amount, 0)
        spouse_additional = where(
            spouse
            & military_additional_age
            & (earned_income > p.additional.threshold.income),
            p.additional.amount,
            0,
        )
        spouse_military_exclusion = tax_unit.sum(
            min_((spouse_base + spouse_additional), military_income)
        )

        # total military exclusions
        return head_military_exclusion + spouse_military_exclusion
