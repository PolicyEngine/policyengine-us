from policyengine_us.model_api import *


class hi_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized

        # Note: All the adjustments are for tax years 2018 through 2025.

        # 1. medical_expense_deduction: same
        hi_medical_expense_deduction = tax_unit(
            "medical_expense_deduction", period
        )

        # 3. interest_deduction:
        # Hawaii did not
        #     (1) suspend the deduction for interest paid on home equity loans
        #     (2) lower the dollar limit on mortgages qualifying for the home mortgage interest deduction
        hi_interest_deductionm = ...
        #

        # 4. charitable_deduction: same
        hi_charitable_deduction = tax_unit("charitable_deduction", period)

        # 5. casualty_loss_deduction
        # Hawaii did not
        #     (1) limit the personal casualty loss deduction for property losses (not used in connection with a trade or business
        #       or transaction entered into for profit)
        #     (2) waive the requirement that casualty losses from qualified disasters exceed 10% of adjusted gross income
        #       to be deductible, and that such losses must exceed $500.
        hi_casualty_loss_deduction = ...


        # Hawaii did not suspend the overall limitation on itemized deductions
        # Cap: $166,800 ($83,400 if married filing separately)
        total_deductions = (
            hi_medical_expense_deduction
            + hi_interest_deductionm
            + hi_charitable_deduction
            + hi_casualty_loss_deduction
        )
        filing_status = tax_unit("filing_status", period)
        
        return min_(total_deductions, p.amount_cap[filing_status])
