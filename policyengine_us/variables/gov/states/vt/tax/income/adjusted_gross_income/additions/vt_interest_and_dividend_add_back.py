from policyengine_us.model_api import *


class vt_interest_and_dividend_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont agi interest and dividend income add back"
    definition_period = YEAR
    defined_for = StateCode.VT
    documentation = "Part of additions to VT AGI over federal AGI. The amount equals to interest and dividend income from non-Vermont state and local obligations which are exempted from federal taxable income are taxable in Vermont."
    reference = [
        {
            "title": "2022 Schedule IN-112 Vermont Tax Adjustments and Credits, PART 1 ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME, Line3",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
        },
        {
            "title": "Instruction for SCHEDULE IN-112 Vermont Tax Adjustments and Credits, Line3",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",
        },
        {
            "title": "Legal Code Titl. 32 V.S.A. § 5811(21)(A)(i)",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
        },
    ]

    def formula(tax_unit, period, parameters):
        # First get the total interest and dividend income received from all state and local obligations exempted from federal tax
        tax_exempted_total_interest_and_dividend_income = add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )
        # Then get interest and dividend income from Vermont state and local obligations exempted from federal tax
        tax_exempted_vt_interest_and_dividend_income = add(
            tax_unit, period, ["tax_exempt_vt_interest_and_dividend_income"]
        )
        return (
            tax_exempted_total_interest_and_dividend_income
            - tax_exempted_vt_interest_and_dividend_income
        )
