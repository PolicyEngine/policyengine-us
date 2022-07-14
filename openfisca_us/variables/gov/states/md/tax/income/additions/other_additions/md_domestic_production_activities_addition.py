## md_domestic_production_activities_addition.py
from openfisca_us.model_api import *

class md_domestic_production_activities_addition(Variable):
    # n. Amount deducted on your federal income tax return for domestic production activities.
    value_type = float
    entity = TaxUnit
    label = "MD domestic production activities"
    documentation = "Amount deducted on your federal income tax return for domestic production activities."
    unit = USD
    definition_period = YEAR