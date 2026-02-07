from policyengine_us.model_api import *


class bond_assets(Variable):
    value_type = float
    entity = Person
    label = "Bond assets"
    documentation = (
        "Value of bonds and government securities. "
        "Imputed from SIPP TVAL_BOND."
    )
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
