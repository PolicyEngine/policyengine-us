from policyengine_us.model_api import *


class tanf_reported(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Reported TANF"
    documentation = (
        "Amount of Temporary Assistance for Needy Families benefit reported."
    )
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
