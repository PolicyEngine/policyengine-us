from policyengine_us.model_api import *


class oasdi_cost(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "OASDI modeled benefits"
    documentation = (
        "Modeled OASDI benefits: members' public social_security, the four "
        "OASDI components after any enabled benefit policies. Excludes "
        "administrative expenses and Railroad Retirement interchange, and "
        "covers only recipients in the household frame."
    )
    unit = USD
    adds = ["social_security"]
