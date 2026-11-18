from policyengine_us.model_api import *


class wa_pte_va_service_connected_rating(Variable):
    value_type = float
    entity = Person
    label = "Combined VA service-connected evaluation rating for the Washington senior and disabled persons property tax exemption"
    documentation = "The combined service-connected evaluation rating from the U.S. Department of Veterans Affairs, as a fraction (0.8 for 80 percent)."
    unit = "/1"
    definition_period = YEAR
    reference = (
        # RCW 84.36.381(3)(a)(ii)(A)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
    )
