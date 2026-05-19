from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC senior disabled property tax relief household income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    adds = ["adjusted_gross_income"]
