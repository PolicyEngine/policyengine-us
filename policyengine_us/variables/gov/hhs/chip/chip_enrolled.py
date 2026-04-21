from policyengine_us.model_api import *


class chip_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "CHIP enrolled"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/chapter-7/subchapter-XXI"
    defined_for = "is_chip_eligible"
    adds = ["takes_up_chip_if_eligible"]
