from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *
from openfisca_us.variables.demographic.household import *


class MedicaidPersonType(Enum):
    ADULT_WITHOUT_DEPENDENT = "Adult without dependent"
    ADULT_WITH_DEPENDENT = "Adult with dependent"
    CHILD_AGE_0 = "Child age 0"
    CHILD_AGE_1_5 = "Child age 1 to 5"
    CHILD_AGE_6_18 = "Child age 6 to 18"


class medicaid_person_type(Variable):
    value_type = Enum
    possible_values = MedicaidPersonType
    default_value = MedicaidPersonType.ADULT_WITHOUT_DEPENDENT
    entity = Person
    definition_period = YEAR
    label = "Medicaid person type"
    documentation = "Person type for Medicaid"


class medicaid_income_threshold(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Medicaid FPL threshold"
    documentation = "Maximum income as a percentage of the federal poverty line to qualify for Medicaid"

    # Get state
    # Get person type
    # Get parameter
    # Return indexed parameter
    def formula(person, period, parameters):
        state_code = person("state_code_str", period)
        person_type = person("medicaid_person_type", period)
        income_threshold = parameters(period).hhs.medicaid
        return income_threshold[state_code][person_type]
