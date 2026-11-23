from policyengine_us.model_api import *


class or_ssp_countable_for_school_meals(Variable):
    value_type = float
    entity = Person
    label = "Oregon state supplement counted for school meals"
    definition_period = MONTH
    unit = USD
    default_value = 0
    defined_for = StateCode.OR
    documentation = (
        "Oregon supplemental cash assistance counted for school meals, excluding "
        "initial placement and room and board payments during absence or incapacity."
    )
    reference = (
        "https://opi.mt.gov/Portals/182/Page%20Files/School%20Nutrition/Meal%20Eligibility/Forms%20and%20Policy/2017eligibilitymanual.pdf#page=34",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0500.pdf",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0575.pdf",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0630.pdf",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0700.pdf",
    )

    def formula(person, period, parameters):
        category = person("or_ssp_category", period)
        c = category.possible_values
        excluded = (
            (category == c.INITIAL_ROOM_BOARD)
            | (category == c.ROOM_BOARD_ABSENCE)
            | (category == c.ROOM_BOARD_INCAPACITY)
        )
        return where(excluded, 0, person("or_ssp", period))
