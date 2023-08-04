from policyengine_us.model_api import *


class az_increased_excise_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Increased excise tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    # From Year 2022 (Line 56)
    reference = "https://azdor.gov/forms/individual/form-140-arizona-resident-personal-income-tax-booklet"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.increased_excise
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        max_income = p.income_threshold[filing_status]
        eligible = agi <= max_income
        tax_unit_size = tax_unit("tax_unit_size", period)
        uncapped_credit = tax_unit_size * p.amount
        return eligible * min_(uncapped_credit, p.max_amount)
