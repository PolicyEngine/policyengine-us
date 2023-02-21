from policyengine_us.model_api import *


class nyc_unincorporated_business_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Unincorporated Business Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
