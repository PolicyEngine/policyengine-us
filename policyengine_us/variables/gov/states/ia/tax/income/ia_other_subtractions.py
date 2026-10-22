from policyengine_us.model_api import *


class ia_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Iowa other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    documentation = (
        "Iowa other subtractions from taxable income reported on Form IA 1040 from 2023, "
        "Schedule 1, Line 11, Column B, and Line 19, excluding the IA 2440 disability income exclusion "
        "(Line 19, code h), which PolicyEngine computes; before 2023, IA 1040 Line 24, "
        "entered as a positive amount."
    )
    # PDF pages 69-71, 74-78 and 30-37
    reference = (
        "https://revenue.iowa.gov/media/4435/download?inline=#page=69",
        "https://revenue.iowa.gov/media/2721/download?inline#page=30",
    )
