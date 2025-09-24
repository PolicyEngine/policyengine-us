from policyengine_us.model_api import *


class ia_subtractions_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa subtractions from taxable income for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.iowa.gov/docs/code/422.7.pdf"
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.taxable_income
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
