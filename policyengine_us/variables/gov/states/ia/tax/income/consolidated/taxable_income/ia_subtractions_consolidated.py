from policyengine_us.model_api import *


class ia_subtractions_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa subtractions from taxable income for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.iowa.gov/docs/code/422.7.pdf"
    defined_for = StateCode.IA

    adds = "gov.states.ia.tax.income.taxable_income.subtractions"
