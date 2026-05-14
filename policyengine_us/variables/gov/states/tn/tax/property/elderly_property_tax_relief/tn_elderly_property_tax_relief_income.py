from policyengine_us.model_api import *


class tn_elderly_property_tax_relief_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee elderly property tax relief income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TN

    adds = ["adjusted_gross_income"]
