from policyengine_us.model_api import *


class cbo_household_income_after_transfers_and_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household income after transfers and taxes"
    documentation = (
        "CBO household income after transfers and taxes: income before "
        "transfers and taxes plus means-tested transfers minus federal taxes."
    )
    definition_period = YEAR
    unit = USD
    adds = [
        "cbo_household_income_before_transfers_and_taxes",
        "cbo_household_means_tested_transfers",
    ]
    subtracts = ["cbo_household_federal_taxes"]
