from policyengine_us.model_api import *


class vt_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VT AGI additions"
    unit = USD
    documentation = "Additions to VT AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = dict(
        title="2022 Schedule IN-112 Vermont Tax Adjustments and Credits, PART 1 ADDITIONS TO FEDERAL ADJUSTED GROSS INCOME",
        href="https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf",
    )
