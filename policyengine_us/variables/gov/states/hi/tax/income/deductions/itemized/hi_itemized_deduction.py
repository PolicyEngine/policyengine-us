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

        # 2. salt_deduction: dont need
        # Hawaii did not limits the deduction for state and local taxes to $10,000 ($5,000 for a married taxpayer filling a separate return)
        # new: The NET amount of taxes withheld from the sale of Hawaii real property interests
        hi_salt_deduction = ...

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

        # 6. miscellaneous_deductions: dont need
        # Hawaii did not suspend all miscellaneous itemized deductions that are subject to the 2% floor
        hi_miscellaneous_deductions = ...

        # Hawaii did not suspend the overall limitation on itemized deductions
        # Cap: $166,800 ($83,400 if married filing separately)
        total_deductions = (
            hi_medical_expense_deduction
            + hi_salt_deduction
            + hi_interest_deductionm
            + hi_charitable_deduction
            + hi_casualty_loss_deduction
            + hi_miscellaneous_deductions
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        itemized_deductions = where(
            separate,
            min_(p.amount_cap.separate, total_deductions),
            min_(p.amount_cap.not_separate, total_deductions),
        )

        return itemized_deductions
