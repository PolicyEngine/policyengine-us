from policyengine_us.model_api import *


class ia_taxable_income_modifications_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa modifications to taxable income for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/media/2746/download?inline",
        "https://www.legis.iowa.gov/docs/code/422.7.pdf",
    )
    defined_for = StateCode.IA

    adds = ["ia_additions_consolidated"]
    subtracts = ["ia_subtractions_consolidated"]
