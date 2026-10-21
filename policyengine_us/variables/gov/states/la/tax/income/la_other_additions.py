from policyengine_us.model_api import *


class la_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA
    documentation = (
        "Louisiana other additions to federal adjusted gross income reported on "
        "Form IT-540, Schedule E, Line 8 (Other Additions to Federal AGI), entered as a positive amount, "
        "excluding items PolicyEngine calculates separately."
    )
    reference = "https://dam.ldr.la.gov/taxforms/IT540i%20WEB(2025)D11.pdf#page=7"
