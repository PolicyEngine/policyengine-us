from policyengine_us.model_api import *


class was_in_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Person was in the a qualifying california foster care institution"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"
