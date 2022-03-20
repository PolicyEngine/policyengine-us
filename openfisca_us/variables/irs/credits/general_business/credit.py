from openfisca_us.model_api import *


class e07400(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "General business credit"
    documentation = "General business credit from Form 3800"
    reference = "https://www.law.cornell.edu/uscode/text/26/38"
    unit = USD
