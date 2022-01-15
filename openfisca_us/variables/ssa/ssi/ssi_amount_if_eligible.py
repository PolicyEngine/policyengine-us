from openfisca_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Supplemental Security Income amount if someone is eligible"
    )
    label = "SSI amount if eligible"
    unit = USD
