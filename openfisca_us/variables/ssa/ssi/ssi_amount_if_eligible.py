from openfisca_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "Supplemental Security Income amount if someone is eligible"
    )
