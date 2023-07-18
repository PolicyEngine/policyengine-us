
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
        ).gov.states.az.tax.income.credits.increased_excise_tax_credit
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        max_income = p.maximum[filing_status]
        eligible = agi <= max_income
        dependents1 = tax_unit("tax_unit_dependents", period)
        dependents2 = p.dependent2[filing_status]
        total_dependents = dependents1 + dependents2
        current_credit = total_dependents * p.credit_based_on_cal_dependents
        return eligible * min_(current_credit, p.max_amount)
