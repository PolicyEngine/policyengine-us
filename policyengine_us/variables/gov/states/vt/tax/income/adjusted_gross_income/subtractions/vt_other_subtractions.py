from policyengine_us.model_api import *


class vt_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    documentation = (
        "Vermont other subtractions from federal adjusted gross income reported on "
        "Schedule IN-112, Part I (Subtractions from Federal Adjusted Gross Income), "
        "entered as a positive amount, excluding subtractions PolicyEngine calculates separately."
    )
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2024.pdf#page=1"
    )
