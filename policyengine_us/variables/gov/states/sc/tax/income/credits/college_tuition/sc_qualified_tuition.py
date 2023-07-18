from policyengine_us.model_api import *


class sc_qualified_tuition(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina Qualified Tuition"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
