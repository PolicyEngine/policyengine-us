from policyengine_us.model_api import *


class ms_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Mississippi other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    documentation = (
        "Mississippi other additions to gross income reported on Form 80-105, "
        "Line 48, Other income (Form 80-108, Part V): the positive Schedule N "
        "income items, with negative entries going in ms_other_subtractions, "
        "entered as a positive amount."
    )
    # PDF pages 12, 16
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12"
