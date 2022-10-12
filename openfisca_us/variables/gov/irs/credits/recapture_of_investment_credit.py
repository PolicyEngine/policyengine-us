from policyengine_us.model_api import *


class recapture_of_investment_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Recapture of Investment Credit"
    unit = USD
    definition_period = YEAR
