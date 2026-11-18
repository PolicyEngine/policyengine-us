from policyengine_us.model_api import *


class school_meal_net_rental_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Net rental income for school meals"
    documentation = (
        "A person's rental income plus their farm rental income. PolicyEngine "
        "nets the two as one net rental income category before school meal "
        "income treats a net loss as zero."
    )
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-04-09/html/2026-06842.htm",
        # PDF pages 27, 29.
        "https://opi.mt.gov/Portals/182/Page%20Files/School%20Nutrition/Meal%20Eligibility/Forms%20and%20Policy/2017eligibilitymanual.pdf#page=27",
    )
    adds = ["rental_income", "farm_rent_income"]
