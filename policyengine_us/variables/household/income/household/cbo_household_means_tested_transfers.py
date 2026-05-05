from policyengine_us.model_api import *


class cbo_household_means_tested_transfers(Variable):
    value_type = float
    entity = Household
    label = "CBO household means-tested transfers"
    documentation = (
        "Means-tested transfers included in CBO household income after "
        "transfers and taxes."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_means_tested_transfers"
