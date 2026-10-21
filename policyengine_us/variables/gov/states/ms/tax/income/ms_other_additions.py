from policyengine_us.model_api import *


class ms_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Mississippi other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    documentation = (
        "Mississippi other additions to gross income reported on "
        "Form 80-105, Line 45 (Other Income), entered as a positive amount."
    )
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=10"
