from policyengine_us.model_api import *


class vt_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    documentation = (
        "Vermont other additions to federal adjusted gross income reported on "
        "Schedule IN-112, Part I (Additions to Federal Adjusted Gross Income), "
        "entered as a positive amount, excluding additions PolicyEngine calculates separately."
    )
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2024.pdf#page=1"
    )
