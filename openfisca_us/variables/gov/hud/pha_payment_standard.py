from openfisca_us.model_api import *


class pha_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD payment standard"
    unit = USD
    documentation = "Payment standard for HUD programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/982.503"
