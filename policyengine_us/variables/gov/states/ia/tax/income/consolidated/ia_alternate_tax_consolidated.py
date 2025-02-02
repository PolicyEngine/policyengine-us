from policyengine_us.model_api import *


class ia_alternate_tax_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa alternate tax for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.iowa.gov/media/2754/download?inline"
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        modified_income = tax_unit("ia_modified_income", period)
        # compute alternate tax following worksheet in the instructions
        p = parameters(period).gov.states.ia.tax.income.alternate_tax
        # ... determine alternate tax deduction
        elderly_head_or_spouse = (
            tax_unit("greater_age_head_spouse", period) >= p.elderly_age
        )
        alt_ded = where(
            elderly_head_or_spouse, p.deduction.elderly, p.deduction.nonelderly
        )
        # ... determine alternate tax amount
        alt_taxinc = max_(0, modified_income - alt_ded)
        return alt_taxinc * p.rate
