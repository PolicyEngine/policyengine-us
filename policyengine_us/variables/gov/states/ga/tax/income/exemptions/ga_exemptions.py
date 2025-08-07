from policyengine_us.model_api import *


class ga_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia Exemptions"
    defined_for = StateCode.GA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=2c053fd5-32c1-4cc1-86b0-36aaade9da5b&pdistocdocslideraccess=true&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A6348-G0H1-DYB7-W3JT-00008-00&pdcomponentid=234187&pdtocnodeidentifier=ABWAALAADAAL&ecomp=k2vckkk&prid=4862391c-e031-443f-ad52-ae86c6bb5ce2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.exemptions
        # Dependent exemptions
        dependents = tax_unit(
            "tax_unit_dependents", period
        )  # Total the number of dependents
        dependent_exemptions = dependents * p.dependent

        # total exemptions
        if p.personal.availability:
            filing_status = tax_unit("filing_status", period)
            personal_exemptions = p.personal.amount[filing_status]
            return personal_exemptions + dependent_exemptions
        return dependent_exemptions
