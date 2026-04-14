from policyengine_us.model_api import *


class bank_account_assets(Variable):
    value_type = float
    entity = Person
    label = "Bank account assets"
    documentation = (
        "Value of checking, savings, and money market accounts. "
        "Imputed from SIPP TVAL_BANK."
    )
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501140200"
