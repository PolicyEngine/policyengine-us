## md_pass_through_not_attributable_to_decoupling_addition.py
from openfisca_us.model_api import *

class md_pass_through_not_attributable_to_decoupling_addition(Variable):
    # b. Net additions to income from pass-through entities not attributable to decoupling.
    value_type = float
    entity = TaxUnit
    label = "MD Pass-Through Not Attributable to Decoupling"
    documentation = "Net additions to income from pass-through entities not attributable to decoupling"
    unit = USD
    definition_period = YEAR