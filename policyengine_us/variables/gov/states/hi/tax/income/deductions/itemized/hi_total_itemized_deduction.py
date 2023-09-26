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

        # Note: All the adjustments are for tax years 2018 through 2025.
        # we need adjustments for medical_expense_deduction, interest_deduction and casualty_loss_deduction
        hi_charitable_deduction = tax_unit("charitable_deduction", period)

        # 1. medical_expense_deduction: worksheet A-1
        hi_medical_expense_deduction = tax_unit(
            "hi_medical_expense_deduction", period
        )

        # 3. interest_deduction: worksheet A-3
        # Hawaii did not
        #     (1) suspend the deduction for interest paid on home equity loans
        #     (2) lower the dollar limit on mortgages qualifying for the home mortgage interest deduction
        #         (Hawaii: 1,000,000, Schedule A: 750,000)
        filing_status = tax_unit("filing_status", period)
        home_mortgage_interest = min_(
            add(tax_unit, period, ["home_mortgage_interest"]),
            p.cap.home_mortgage_interest_cap[filing_status],
        )
        investment_interest = tax_unit("investment_income_form_4952", period)
        hi_interest_deduction = home_mortgage_interest + investment_interest

        # 5. casualty_loss_deduction: worksheet A-5
        hi_casualty_loss_deduction = tax_unit(
            "hi_casualty_loss_deduction", period
        )

        return (
            hi_charitable_deduction
            + hi_medical_expense_deduction
            + hi_interest_deduction
            + hi_casualty_loss_deduction
        )
