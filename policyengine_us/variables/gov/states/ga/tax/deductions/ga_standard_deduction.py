from policyengine_us.model_api import *


class ga_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "georgia standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        base_amt = p.base_amount[filing_status]
        # $1,300 for self bild and self aged each
        head = person("is_tax_unit_head", period)
        blind = person("is_blind", period)
        aged = person("age", period) >= p.aged.age_eligible
        extra_amt_head = tax_unit.sum(
            head * blind * p.blind.self + head * aged * p.aged.self
        )
        # $1,300 for spouse bild and self aged each
        spouse = person("is_tax_unit_spouse", period)
        extra_amt_spouse = where(
            filing_status == status.JOINT,
            tax_unit.sum(
                spouse * blind * p.blind.self + spouse * aged * p.aged.self
            ),
            0,
        )
        # total extra deduction
        extra_amt = extra_amt_head + extra_amt_spouse
        return base_amt + extra_amt
