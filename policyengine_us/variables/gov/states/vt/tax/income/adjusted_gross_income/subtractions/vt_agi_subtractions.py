from policyengine_us.model_api import *


class vt_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont AGI subtractions"
    unit = USD
    documentation = "Subtractions from Vermont AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1"  # PART 1 SUBTRACTIONS TO FEDERAL ADJUSTED GROSS INCOME
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(B)(i), (C)(iv), (B)(vi), (B)(ii), (B)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        # Get interest income from U.S. obligations
        us_govt_interest = tax_unit("us_govt_interest", period)
        # Get Vermont medical expense deductions
        vt_medical_expense_deduction = tax_unit(
            "vt_medical_expense_deduction", period
        )
        # Get student loan interest
        student_loan_interest = add(
            tax_unit, period, ["student_loan_interest"]
        )
        # Get capital gains exclusion
        capital_gains_excluded_from_taxable_income = tax_unit(
            "capital_gains_excluded_from_taxable_income", period
        )
        # Get Vermont retirement income exemption
        vt_retirement_income_exemption = tax_unit(
            "vt_retirement_income_exemption", period
        )
        return (
            us_govt_interest
            + vt_medical_expense_deduction
            + student_loan_interest
            + capital_gains_excluded_from_taxable_income
            + vt_retirement_income_exemption
        )
