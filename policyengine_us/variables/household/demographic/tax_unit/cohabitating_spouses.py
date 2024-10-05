from policyengine_us.model_api import *


class cohabitating_spouses(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Cohabitating spouses"
    documentation = (
        "Whether spouses in joint or separate tax units are cohabitating."
    )
