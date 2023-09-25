from policyengine_us.model_api import *


class hi_total_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii total itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_deductions = parameters(period).gov.irs.deductions

        # Note: All the adjustments are for tax years 2018 through 2025.
        # we need adjustments for interest_deduction and casualty_loss_deduction
        same_deductions = [
            deduction
            for deduction in p_deductions.itemized_deductions
            if deduction
            not in [
                "medical_expense_deduction",
                "salt_deduction",
                "interest_deduction",
                "casualty_loss_deduction",
            ]
        ]
        federal_deductions = add(tax_unit, period, same_deductions)

        # 1. medical_expense_deduction: worksheet A-1
        # use hi_agi instead of agi
        medical_expense = add(tax_unit, period, ["medical_expense"])
        hi_agi = tax_unit("hi_agi", period)
        medical_agi_amount = max_(
            0, p_deductions.itemized.medical.floor * hi_agi
        )
        hi_medical_expense_deduction = max_(
            0, medical_expense - medical_agi_amount
        )

        # 3. interest_deduction: worksheet A-3
        # Hawaii did not
        #     (1) suspend the deduction for interest paid on home equity loans
        #     (2) lower the dollar limit on mortgages qualifying for the home mortgage interest deduction
        #         (Hawaii: 1,000,000, Schedule A: 750,000)
        filing_status = tax_unit("filing_status", period)
        home_mortgage_interest = min_(
            add(tax_unit, period, ["home_mortgage_interest"]),
            p.home_mortgage_interest_cap[filing_status],
        )
        investment_interest = add(tax_unit, period, ["investment_interest"])
        hi_interest_deduction = home_mortgage_interest + investment_interest

        # 5. casualty_loss_deduction: worksheet A-5
        # Hawaii did not
        #     (1) limit the personal casualty loss deduction for property losses (not used in connection with a trade or business
        #       or transaction entered into for profit)
        #     (2) waive the requirement that casualty losses from qualified disasters exceed 10% of adjusted gross income
        #       to be deductible, and that such losses must exceed $500.
        casualty_loss = add(tax_unit, period, ["casualty_loss"])
        casualty_agi_amount = max_(
            0, p_deductions.itemized.casualty.floor * hi_agi
        )
        hi_casualty_loss_deduction = max(
            0, casualty_loss - casualty_agi_amount
        )

        total_deductions = (
            federal_deductions
            + hi_medical_expense_deduction
            + hi_interest_deduction
            + hi_casualty_loss_deduction
        )

        return total_deductions
