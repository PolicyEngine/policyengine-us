from policyengine_us.model_api import *


class md_frederick_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Frederick County local income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=25"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("md_taxable_income", period)
        # Fixed rate: entire income * bracket rate.
        # The rate is zero outside Frederick County.
        rate = tax_unit("md_frederick_county_tax_rate", period)
        return taxable_income * rate
