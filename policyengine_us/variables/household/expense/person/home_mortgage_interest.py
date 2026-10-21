from policyengine_us.model_api import *


class home_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on a home mortgage"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "Home mortgage interest on debt secured by the principal residence, "
        "including interest reported and not reported on federal Form 1098. "
        "Report interest on a second qualified residence, such as a vacation "
        "home, in second_residence_mortgage_interest instead. Interest whose "
        "residence is unknown is treated as principal-residence interest."
    )
