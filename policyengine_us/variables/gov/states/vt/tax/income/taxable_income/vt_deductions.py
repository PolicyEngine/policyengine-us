from policyengine_us.model_api import *


class vt_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf",  # Line4
        "http://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(C)(ii)(iii)
    )
    defined_for = StateCode.VT

    adds = ["vt_standard_deductions"]
