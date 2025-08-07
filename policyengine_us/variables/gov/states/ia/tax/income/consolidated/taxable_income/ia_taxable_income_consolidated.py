from policyengine_us.model_api import *


class ia_taxable_income_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa taxable income for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/media/2746/download?inline",
        "https://www.legis.iowa.gov/docs/code/422.7.pdf",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        fed_taxable_income = tax_unit("taxable_income", period)
        modifications = tax_unit(
            "ia_taxable_income_modifications_consolidated", period
        )
        # Modifications include additions and subtractions
        return max_(0, fed_taxable_income + modifications)
