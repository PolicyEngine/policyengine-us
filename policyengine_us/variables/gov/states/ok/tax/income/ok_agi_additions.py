from policyengine_us.model_api import *


class ok_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK
