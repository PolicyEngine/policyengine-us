from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in NYC"
    # No formula by design given that in_nyc is included in CPS datasets.
    # For details, see the add_household_variables method in the
    # policyengine_us/data/datasets/cps/cps.py module.
