from policyengine_us.model_api import *


class hi_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=19"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_deductions = parameters(period).gov.irs.deductions
        person = tax_unit.members

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
        medical_expense = add(tax_unit, period, ["medical_expense"])
        hi_agi = tax_unit("hi_agi", period)
        medical_agi_amount = max_(0, p.medical_rate * hi_agi)
        hi_medical_expense_deduction = max_(
            0, medical_expense - medical_agi_amount
        )

        # 3. interest_deduction: worksheet A-3
        # Hawaii did not
        #     (1) suspend the deduction for interest paid on home equity loans
        #     (2) lower the dollar limit on mortgages qualifying for the home mortgage interest deduction
        filing_status = tax_unit("filing_status", period)
        # Section 163(h)(3)(F)
        home_mortgage_interest = min_(
            add(tax_unit, period, ["home_mortgage_interest"]),
            p.home_mortgage_interest_cap[filing_status],
        )
        investment_interest = add(tax_unit, period, ["investment_interest"])
        hi_interest_deduction = home_mortgage_interest + investment_interest

        # 5. casualty_loss_deduction
        # Hawaii did not
        #     (1) limit the personal casualty loss deduction for property losses (not used in connection with a trade or business
        #       or transaction entered into for profit)
        #     (2) waive the requirement that casualty losses from qualified disasters exceed 10% of adjusted gross income
        #       to be deductible, and that such losses must exceed $500.
        casualty_loss = add(tax_unit, period, ["casualty_loss"])
        casualty_agi_amount = max_(0, p.casualty_rate * hi_agi)
        hi_casualty_loss_deduction = max(
            0, casualty_loss - casualty_agi_amount
        )

        total_deductions = (
            federal_deductions
            + hi_medical_expense_deduction
            + hi_interest_deduction
            + hi_casualty_loss_deduction
        )
        print(federal_deductions)
        print(hi_medical_expense_deduction)
        print(hi_interest_deduction)
        print(hi_casualty_loss_deduction)

        # Hawaii did not suspend the overall limitation on itemized deductions
        # Cap: $166,800 ($83,400 if married filing separately)
        # You may not be able to deduct all of your itemized deductions if agi reach the cap
        # need to calculate the reduced itemized deductions
        itemized_eligible = hi_agi < p.agi_cap[filing_status]

        return where(
            itemized_eligible,
            total_deductions,
            tax_unit("hi_reduced_itemized_deduction", period),
        )
