from openfisca_us.model_api import *


class Sex(Enum):
    MALE = ("Male",)
    FEMALE = "Female"


class sex(Variable):
    value_type = Enum
    entity = Person
    label = "Sex"
    possible_values = Sex
    default_value = Sex.MALE
    definition_period = YEAR
