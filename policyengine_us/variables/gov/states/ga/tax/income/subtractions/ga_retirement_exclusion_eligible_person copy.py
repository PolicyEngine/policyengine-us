from policyengine_us.model_api import *


class ga_retirement_exclusion_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Georgia retirement exclusion younger cap"
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download"
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )
    defined_for = StateCode.GA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ga.tax.income.agi.exclusions.retirement
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        age_younger = (age >= p.age.younger) & (age < p.age.older)
        # age_older = age >= p.age.older
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # older_cap_eligible = head_or_spouse & age_older
        # Disabled filers can qualify for the younger age cap amount if they are below the age threshold.
        below_age_younger = age < p.age.younger
        disabled = person("is_disabled", period)
        disabled_eligible = below_age_younger & disabled
        return head_or_spouse & (age_younger | disabled_eligible)
        # return  older_cap_eligible or younger_cap_eligible
