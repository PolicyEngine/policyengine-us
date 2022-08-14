from openfisca_us.model_api import *


class nonbusiness_energy_property_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Nonbusiness energy property credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"
