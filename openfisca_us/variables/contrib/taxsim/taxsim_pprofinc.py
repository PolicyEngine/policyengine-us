from openfisca_us.model_api import *


class taxsim_pprofinc(Variable):
    value_type = float
    entity = TaxUnit
    label = "SSTB income for the primary taxpayer (TAXSIM). Assumed zero."
    unit = USD
    definition_period = YEAR
