from policyengine_us.model_api import *


class vt_bonus_depreciation_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT bonus depreciation add back"
    definition_period = YEAR
    documentation = "Add back for the difference between the depreciation calculated by standard MACRS methods and the depreciation calculated using the federal bonus depreciation for assets placed in service in 2022."
    reference = [
        {
            "title": "2022 Schedule IN-112 Vermont Tax Adjustments and Credits, PART 1 ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME, Line4",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
        },
        {
            "title": "Instruction for SCHEDULE IN-112 Vermont Tax Adjustments and Credits, Line4",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",
        },
        {
            "title": "Technical Bulletin TB-44, Disallowance of Bonus Depreciation Provisions of Federal Economic Stimulus Act of 2008",
            "href": "https://tax.vermont.gov/sites/tax/files/documents/TB44.pdf",
        },
    ]
