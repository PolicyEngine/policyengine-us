from openfisca_us.model_api import *


class medicaid(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Estimated benefit amount from Medicaid"
    label = "Medicaid benefit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
