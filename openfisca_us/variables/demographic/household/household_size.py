from openfisca_us.model_api import *

class HouseholdSize(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13
    FOURTEEN = 14
    FIFTEEN = 15
    SIXTEEN = 16
    SEVENTEEN = 17
    EIGHTEEN = 18
    NINETEEN = 19
    TWENTY = 20

class household_size(Variable):
    value_type = Enum
    possible_values = HouseholdSize
    default_value = HouseholdSize.ONE
    entity = Household
    label = "Household size"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        return household.nb_persons()