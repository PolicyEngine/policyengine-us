from policyengine_us.model_api import *


class vt_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf",
        "http://legislature.vermont.gov/statutes/section/32/151/05811",
    )
    defined_for = StateCode.VT

    adds = ["vt_personal_exemptions"]
