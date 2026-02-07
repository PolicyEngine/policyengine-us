from policyengine_us.model_api import *


class stock_assets(Variable):
    value_type = float
    entity = Person
    label = "Stock assets"
    documentation = (
        "Value of stocks and mutual funds. " "Imputed from SIPP TVAL_STMF."
    )
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501140220"
