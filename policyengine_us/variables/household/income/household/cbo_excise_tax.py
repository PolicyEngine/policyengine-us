from policyengine_us.model_api import *


class cbo_excise_tax(Variable):
    value_type = float
    entity = Household
    label = "Allocated excise tax for CBO household income"
    documentation = (
        "Household federal excise tax burden used in the CBO household "
        "income framework."
    )
    definition_period = YEAR
    unit = USD
