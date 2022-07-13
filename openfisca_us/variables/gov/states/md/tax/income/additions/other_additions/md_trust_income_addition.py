## md_trust_income_addition.py
from openfisca_us.model_api import *

class md_trust_income_addition(Variable):
    # c. Net additions to income from a trust as reported by the fiduciary.
    value_type = float
    entity = TaxUnit
    label = "MD Trust Income"
    documentation = (
        "Net additions to income from a trust as reported by the fiduciary"
    )
    unit = USD
    definition_period = YEAR