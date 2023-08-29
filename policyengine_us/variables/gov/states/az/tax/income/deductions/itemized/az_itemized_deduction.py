from policyengine_us.model_api import *


class az_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Itemized Deductions"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1042/",
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form",
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction
            not in [
                "salt_deduction",
                "medical_expense_deduction",
                "charitable_deduction",
            ]
        ]
        federal_deductions = add(tax_unit, period, deductions)
        # Adjustment to Medical and Dental Expresses
        medical_expense = add(tax_unit, period, ["medical_expense"])
        medical_expense_deduction = tax_unit(
            "medical_expense_deduction", period
        )
        az_medical_expense_deduction = where(
            medical_expense >= medical_expense_deduction,
            medical_expense - medical_expense_deduction,
            medical_expense_deduction - medical_expense,
        )
        charitable_deduction = tax_unit("az_charitable_deduction", period)

        # Adjustment to Interest Deduction
        # mortgage_interest = the amount of mortgage interest you paid for 2022 that is equal to
        # the amount of federal credit, if you received a federal credit for interest paid on
        # mortgage credit certificates (from federal Form 8396).

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming a credit under Arizona law
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_chartiable_contributions_credit", period
        )

        charitable_deduction_allowed = where(
            charitable_contributions_credit > 0, 0, charitable_deduction
        )

        # Adjustment to State Income Taxes - add back real estate taxes
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])

        return (
            federal_deductions
            + az_medical_expense_deduction
            + charitable_deduction_allowed
            + real_estate_taxes
        )


# Make a az_chartiable_contributions_credit.py file in credits
