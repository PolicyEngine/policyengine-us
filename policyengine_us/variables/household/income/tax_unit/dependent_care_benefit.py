from policyengine_us.model_api import *


class dependent_care_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Dependent care benefits received"
    unit = USD
    definition_period = YEAR
