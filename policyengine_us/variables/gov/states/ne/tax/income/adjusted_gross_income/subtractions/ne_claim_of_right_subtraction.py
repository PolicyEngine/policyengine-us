from policyengine_us.model_api import *


class ne_claim_of_right_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska claim of right repayment subtraction"
    unit = USD
    documentation = (
        "Nebraska excludes from federal adjusted gross income any amount "
        "repaid for which a reduction in federal tax is allowed under 26 "
        "U.S.C. 1341(a)(5) (Schedule I, claim of right repayment). Under "
        "section 1341(a)(4) the repayment is a federal itemized deduction "
        "instead, which Nebraska itemized deductions follow."
    )
    definition_period = YEAR
    reference = (
        # Neb. Rev. Stat. 77-2716(7)
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2716",
        # 2025 Nebraska Individual Income Tax Booklet, Schedule I, line 26
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=26",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(credit_applies, repayment, 0)
