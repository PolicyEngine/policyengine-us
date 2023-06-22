# Questions:
# 1. Doesn't mention widow?
# 2. Should I remove "federal"?

# Some details that don't include in the coding:
# 1. valid SSN for employement
# 2. prison issues
# 3. You are not claimed as a dependent by any other taxpayer
# 4. The credit cannot exceed $100 per household. Do not claim this credit if someone else in your household has already claimed $100 of the credit. If someone else in your household has claimed less than $100, you may claim the credit as long as all credit claims filed from your household do not exceed $100

from policyengine_us.model_api import *


class az_increased_excise_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "AZ Totaling Payments and Refundable Credits - increased excise tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://azdor.gov/forms/individual/form-140-arizona-resident-personal-income-tax-booklet"  # From Year 2022 (Line 56)

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.increased_excise_tax_credit
        agi = tax_unit(
            "adjusted_gross_income", period
        )  # should I remove "federal"?
        filing_status = tax_unit("filing_status", period)
        max_income = p.maximum[filing_status]
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                # filing_status == status.WIDOW,
            ],
            [
                p.maximum,
                p.maximum,
                p.maximum,
                p.maximum,
                # p.maximum,
            ],
        )
        eligible = line12 <= max_income
        dependents1 = tax_unit("tax_unit_dependents", period)
        dependents2 = p.dependent2[filing_status]
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                # filing_status == status.WIDOW,
            ],
            [
                p.dependent2,
                p.dependent2,
                p.dependent2,
                p.dependent2,
                # p.dependent2,
            ],
        )
        total_dependents = dependents1 + dependents2
        current_credit = total_dependents * p.credit_based_on_cal_dependents
        return eligible * min_(current_credit, p.max_amount)
