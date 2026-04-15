from policyengine_us.model_api import *


class cbo_corporate_income_tax(Variable):
    value_type = float
    entity = Household
    label = "Allocated corporate income tax for CBO household income"
    documentation = (
        "Household corporate income tax burden used in the CBO household "
        "income framework. CBO allocates 75 percent in proportion to capital "
        "income and 25 percent in proportion to labor income."
    )
    definition_period = YEAR
    unit = USD
