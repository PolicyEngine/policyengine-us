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
        # This logic is only required if we have a concept of premiums withheld from social security
        # social_security_benefits = tax_unit("tax_unit_ssi", period)
        # taxable_ss_benefits = tax_unit("tax_unit_taxable_social_security")
        # taxable_ss_ratio = taxable_ss_benefits / social_security_benefits

        person = tax_unit.members
        total_health_insurance_premiums = add(
            person, period, ["health_insurance_premiums"]
        )  # 'self_employed_health_insurance_premiums'

        # Federal Schedule A, Line 1
        med_dental_out_of_pocket = person(
            "medical_out_of_pocket_expenses", period
        )
        # Federal Schedule A, Line 4
        med_expense_deduction = tax_unit("medical_expense_deduction", period)

        med_expense_deducted_ratio = where(
            med_dental_out_of_pocket > 0,
            round(med_expense_deduction / med_dental_out_of_pocket, 3),
            0,
        )
        premium_portion = (
            total_health_insurance_premiums * med_expense_deducted_ratio
        )  # Line 13 of MO Form 5695,absolutely no clue what to call this
        itemized_premiums_amount = (
            total_health_insurance_premiums - premium_portion
        )  # same here, the logic is correct but unclear the purpose... TBD

        itemizes = tax_unit("itemizes", period)
        itemized_premiums = itemizes * total_health_insurance_premiums
        taxable_income = tax_unit("taxable_income", period)

        return where(
            itemized_premiums > 0,
            min_(itemized_premiums_amount, taxable_income),
            min_(total_health_insurance_premiums, taxable_income),
        )
