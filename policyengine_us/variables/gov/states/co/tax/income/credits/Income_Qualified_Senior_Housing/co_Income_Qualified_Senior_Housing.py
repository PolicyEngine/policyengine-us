from policyengine_us.model_api import *


class co_income_qualified_senior_housing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado senior citizen credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit,
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.Income_Qualified_Senior_Housing
        tax_unit_size = tax_unit("tax_unit_size", period)
        return where(
            tax_unit_size == 0, p.base_personal, p.personal * tax_unit_size
        )