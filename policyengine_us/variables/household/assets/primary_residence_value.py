from policyengine_us.model_api import *


class primary_residence_value(Variable):
    value_type = float
    entity = Person
    label = "Primary residence value"
    documentation = (
        "Market value of the person's primary residence, not assessed value."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    reference = (
        "https://www.census.gov/programs-surveys/acs/microdata/documentation.html"
    )
