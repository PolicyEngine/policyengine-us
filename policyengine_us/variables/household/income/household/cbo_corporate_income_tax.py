from policyengine_us.model_api import *


class cbo_corporate_income_tax(Variable):
    value_type = float
    entity = Household
    label = "Optional corporate income tax incidence input for CBO analysis"
    documentation = (
        "Optional household corporate income tax incidence input for "
        "CBO-style analysis. This is reserved for future explicit incidence "
        "allocation and is not included in the default PE-US CBO benchmark."
    )
    definition_period = YEAR
    unit = USD
