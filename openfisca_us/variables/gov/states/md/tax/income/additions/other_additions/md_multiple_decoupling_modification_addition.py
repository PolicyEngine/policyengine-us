## md_multiple_decoupling_modification_addition.py
from openfisca_us.model_api import *

class md_multiple_decoupling_modification_addition(Variable):
    # dm. Net addition modification from multiple decoupling provisions. See the table at the bottom of Form 500DM for the line numbers and code letters to use.
    value_type = float
    entity = TaxUnit
    label = "MD multiple decoupling modification"
    documentation = "Net addition modification from multiple decoupling provisions. See the table at the bottom of Form 500DM for the line numbers and code letters to use."
    unit = USD
    definition_period = YEAR