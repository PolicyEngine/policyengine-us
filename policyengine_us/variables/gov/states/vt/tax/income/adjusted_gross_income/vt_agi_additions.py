from policyengine_us.model_api import *


class vt_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont AGI additions"
    unit = USD
    documentation = "Additions to Vermont adjusted gross income"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1"
        "https://legislature.vermont.gov/statutes/section/32/151/05811"
    )

    adds = ["tax_exempt_interest_income"]
