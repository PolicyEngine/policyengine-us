from policyengine_us.model_api import *


class vt_interest_and_dividend_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT Interest and dividend income add back"
    definition_period = YEAR
    documentation = "Add back for Interest and dividend income from Non-Vermont State and Local Obligations"
    reference = [
        {
            "title": "2022 Schedule IN-112 Vermont Tax Adjustments and Credits, PART 1 ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME, Line3",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
        },
        {
            "title": "Instruction for SCHEDULE IN-112 Vermont Tax Adjustments and Credits, Line3",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",
        },
    ]

    def formula(tax_unit, period, parameters):
        total_interest_and_dividend = add(
            tax_unit, period, ["interest_income", "dividend_income"]
        )

        vt_interest_and_dividend = add(
            tax_unit, period, ["vt_interest_and_dividend"]
        )
        return total_interest_and_dividend - vt_interest_and_dividend
