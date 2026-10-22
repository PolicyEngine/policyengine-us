from policyengine_us.model_api import *


class ia_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Iowa other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    documentation = (
        "Iowa other additions to taxable income reported on Form IA 1040 from 2023, "
        "Schedule 1, Line 11, Column A; before 2023, IA 1040 Line 14, entered as a positive amount, "
        "excluding miscellaneous income, which PolicyEngine already includes."
    )
    # PDF pages 69-71 and 20-22
    reference = (
        "https://revenue.iowa.gov/media/4435/download?inline=#page=69",
        "https://revenue.iowa.gov/media/2721/download?inline#page=20",
    )
