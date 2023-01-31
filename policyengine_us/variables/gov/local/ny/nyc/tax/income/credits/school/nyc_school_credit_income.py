from policyengine_us.model_api import *


class nyc_school_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income used for school tax credit"
    unit = USD
    definition_period = YEAR
