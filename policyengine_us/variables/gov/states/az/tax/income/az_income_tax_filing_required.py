from policyengine_us.model_api import *


class az_income_tax_filing_required(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Arizona income tax filing required"
    documentation = "Whether the tax unit is required to file an Arizona income tax return."
    reference = (
        "https://azdor.gov/individuals/income-tax-filing-assistance/"
        "filing-individual-returns"
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income

        filing_status = tax_unit("az_filing_status", period)
        gross_income = tax_unit("adjusted_gross_income", period)

        threshold = p.filing_requirement[filing_status]

        return gross_income > threshold
