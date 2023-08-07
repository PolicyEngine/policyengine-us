from policyengine_us.model_api import *


class care_and_support_costs(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Amount of total costs for care and support for seniors"
