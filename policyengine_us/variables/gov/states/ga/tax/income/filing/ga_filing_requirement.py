from policyengine_us.model_api import *


class ga_is_filing_requirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "georgia filing requirement"
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )

    def formula(tax_unit, period):
        person = tax_unit.members
        ga_standard_deduction = tax_unit("ga_standard_deduction", period)
        ga_exemptions = tax_unit("ga_exemptions", period)
        ga_earned_income = tax_unit.sum(person("earned_income", period))
        is_filing_requirment = (
            ga_standard_deduction + ga_exemptions
        ) > ga_earned_income

        return is_filing_requirement
