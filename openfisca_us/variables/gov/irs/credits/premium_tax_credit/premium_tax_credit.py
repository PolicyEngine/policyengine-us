from openfisca_us.model_api import *


class premium_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Premium Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"
