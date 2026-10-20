from policyengine_us.model_api import *


class ky_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Kentucky other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    documentation = (
        "Kentucky other additions to federal adjusted gross income reported on "
        "Schedule M, Part I, Line 5 (Other additions), entered as a positive amount."
    )
    reference = (
        "https://revenue.ky.gov/Forms/740%20instructions%20packet%20(2024).pdf#page=27"
    )
