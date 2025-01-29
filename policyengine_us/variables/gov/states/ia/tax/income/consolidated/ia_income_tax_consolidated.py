from policyengine_us.model_api import *


class ia_income_tax_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/media/2746/download?inline",
        "https://www.legis.iowa.gov/docs/code/422.7.pdf",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        reg_tax = tax_unit("ia_regular_tax_consolidated", period)
        alt_tax_eligible = tax_unit("ia_alternate_tax_eligible", period)
        alt_tax = tax_unit("ia_alternate_tax_consolidated", period)
        smaller_tax = min_(reg_tax, alt_tax)
        return where(alt_tax_eligible, smaller_tax, reg_tax)
