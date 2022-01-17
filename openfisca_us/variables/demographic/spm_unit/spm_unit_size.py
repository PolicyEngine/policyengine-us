from openfisca_us.model_api import *


class spm_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SPM unit size"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit.nb_persons()


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
    unit = USD
    documentation = "Dummy variable, used for parameter nesting"
    definition_period = ETERNITY
