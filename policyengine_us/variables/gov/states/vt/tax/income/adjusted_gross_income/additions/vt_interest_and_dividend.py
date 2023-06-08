from policyengine_us.model_api import *


class vt_interest_and_dividend(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT Interest and dividend income"
    definition_period = YEAR
    documentation = "The interest and dividend income from Vermont obligation"
    reference = [
        {
            "title": "2022 Schedule IN-112 Vermont Tax Adjustments and Credits, PART 1 ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME, Line2",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
        },
        {
            "title": "Instruction for SCHEDULE IN-112 Vermont Tax Adjustments and Credits, Line2",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",
        },
    ]
