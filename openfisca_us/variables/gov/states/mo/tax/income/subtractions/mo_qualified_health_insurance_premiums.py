from openfisca_us.model_api import *


class mo_qualified_health_insurance_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO qualified healh insurance premiums"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/5695.pdf",  # Form MO 5695
        "https://www.irs.gov/pub/irs-pdf/f1040sa.pdf",  # Federal Form 1040 Schedule A
        "https://www.irs.gov/pub/irs-pdf/f1040.pdf",  # Federal Form 1040
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        total_health_insurance_premiums = add(
            tax_unit, period, ["health_insurance_premiums"]
        )  # total_health_insurance_premiums is also a primary input to the MO side of calculation, MO Form 5695, Line 8
        # Federal Schedule A, Line 4
        med_expense_deduction = tax_unit("medical_expense_deduction", period)

        # the ratio of federal medical expense deduction to total medical expenses (out of pocket + premiums)
        # need division because med_dental_out_of_pocket is in federal tax, but no MO tax
        # this ratio is then used to scale the health_insurance_premium amount that can be claimed
        total_health_expenses = add(
            tax_unit,
            period,
            ["medical_out_of_pocket_expenses", "health_insurance_premiums"],
        )
        med_expense_deducted_ratio = where(
            total_health_expenses > 0,
            med_expense_deduction / total_health_expenses,
            0,
        )

        # Line 13 of MO Form 5695, represents the portion of medical expenses already deducted via federal tax itemization
        deducted_portion = (
            total_health_insurance_premiums * med_expense_deducted_ratio
        )
        # subtracts the portion of premiums already deducted from federal tax
        itemized_premiums_amount = (
            total_health_insurance_premiums - deducted_portion
        )

        itemizes = tax_unit("tax_unit_itemizes", period)
        # Cap at federal taxable income.
        taxable_income = tax_unit("taxable_income", period)

        return where(
            itemizes,
            min_(itemized_premiums_amount, taxable_income),
            min_(total_health_insurance_premiums, taxable_income),
        )
