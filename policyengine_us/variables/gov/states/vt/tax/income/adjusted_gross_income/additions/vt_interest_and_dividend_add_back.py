from policyengine_us.model_api import *


class vt_interest_and_dividend_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont agi interest and dividend income add back"
    definition_period = YEAR
    defined_for = StateCode.VT
    documentation = "Part of additions to VT AGI over federal AGI. The amount equals to interest and dividend income from non-Vermont state and local obligations which are exempted from federal taxable income are taxable in Vermont."
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1"  # Part I ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=1"
        "https://legislature.vermont.gov/statutes/section/32/151/05811"
    )

    def formula(tax_unit, period, parameters):
        # First get the total interest and dividend income received from all state and local obligations exempted from federal tax
        tax_exempted_total_interest_and_dividend_income = add(
            tax_unit,
            period,
            ["tax_exempt_interest_income"],
        )
        # Then get interest and dividend income from Vermont state and local obligations exempted from federal tax
        vt_tax_exempt_interest_and_dividend_income = add(
            tax_unit, period, ["vt_tax_exempt_interest_and_dividend_income"]
        )
        return (
            tax_exempted_total_interest_and_dividend_income
            - vt_tax_exempt_interest_and_dividend_income
        )
