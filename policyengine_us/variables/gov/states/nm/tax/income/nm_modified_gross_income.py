from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
