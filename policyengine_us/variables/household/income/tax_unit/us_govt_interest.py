from policyengine_us.model_api import *


class us_govt_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest on U.S. government obligations"
    unit = USD
    definition_period = YEAR
    documentation = "Interest on U.S. government obligations such as U.S. savings bonds, U.S. Treasury bills, and U.S. government certificates."

    adds = ["us_govt_interest_person"]
