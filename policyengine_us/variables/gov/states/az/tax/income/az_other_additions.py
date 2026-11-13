from policyengine_us.model_api import *


class az_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    documentation = (
        "Arizona other additions to Arizona gross income reported on "
        "Form 140, Line 18 (Other Additions to Arizona Gross Income), entered as a positive amount."
    )
    reference = "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=9"
