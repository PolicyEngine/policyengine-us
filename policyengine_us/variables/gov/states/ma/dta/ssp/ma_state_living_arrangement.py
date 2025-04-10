from policyengine_us.model_api import *


class MAStateLivingArrangement(Enum):
    FULL_COST = "Full cost of living"
    SHARED_EXPENSES = "Shared expenses"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    REST_HOME = "Rest home"
    MEDICAID_FACILITY = "Medicaid facility"
    ASSISTED_LIVING = "Assisted living"


class ma_state_living_arrangement(Variable):
    value_type = Enum
    entity = Household
    label = "Massachusetts State Living Arrangement"
    definition_period = YEAR
    defined_for = StateCode.MA
    possible_values = MAStateLivingArrangement
    default_value = MAStateLivingArrangement.FULL_COST
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-327-220"
    )
