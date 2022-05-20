from openfisca_us.model_api import *


class StateLivingArrangement(Enum):
    FULL_COST = "Full cost of living"
    SHARED_EXPENSES = "Shared expenses"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    REST_HOME = "Rest home"
    MEDICAID_FACILITY = "Medicaid facility"
    ASSISTED_LIVING = "Assisted living"


class state_living_arrangement(Variable):
    value_type = Enum
    entity = Household
    label = "Federal living arrangement"
    definition_period = YEAR
    possible_values = StateLivingArrangement
    default_value = StateLivingArrangement.FULL_COST
