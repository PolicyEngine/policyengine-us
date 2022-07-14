## md_oil_percentage_depletion_allowance_addition.py
from openfisca_us.model_api import *

class md_oil_percentage_depletion_allowance_addition(Variable):
    # f. Oil percentage depletion allowance claimed under IRC Section 613.
    value_type = float
    entity = TaxUnit
    label = "MD Oil Percentage Depletion Allowance"
    documentation = (
        "Oil percentage depletion allowance claimed under IRC Section 613"
    )
    unit = USD
    definition_period = YEAR