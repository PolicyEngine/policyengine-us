## md_pass_through_entity_decoupling_modification_addition.py
from openfisca_us.model_api import *

class md_pass_through_entity_decoupling_modification_addition(Variable):
    # dp. Net addition decoupling modification from a pass-through entity. See Form 500DM.
    value_type = float
    entity = TaxUnit
    label = "MD pass-through entity decoupling modification"
    documentation = "Net addition decoupling modification from a pass-through entity. See Form 500DM."
    unit = USD
    definition_period = YEAR