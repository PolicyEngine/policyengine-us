from policyengine_us.model_api import *


class id_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    documentation = (
        "Idaho other additions to federal adjusted gross income reported on "
        "Form 39R, Part A, Line 6 (Other additions), entered as a positive amount."
    )
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=42"
