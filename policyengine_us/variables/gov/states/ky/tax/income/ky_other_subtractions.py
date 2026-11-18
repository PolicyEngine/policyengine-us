from policyengine_us.model_api import *


class ky_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Kentucky other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    documentation = (
        "Kentucky other subtractions from federal adjusted gross income reported on "
        "Schedule M, Part II, Line 14 (Other subtractions), entered as a positive amount. "
        "Do not include state tax refunds, U.S. government interest, pension exclusions, "
        "Social Security, or military pay, which PolicyEngine computes separately."
    )
    reference = (
        "https://revenue.ky.gov/Forms/740%20instructions%20packet%20(2024).pdf#page=29"
    )
