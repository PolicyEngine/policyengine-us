from policyengine_us.model_api import *


class wa_pte_receives_va_disability_compensation(Variable):
    value_type = bool
    entity = Person
    label = "Entitled to and receiving VA compensation for a service-connected disability for the Washington senior and disabled persons property tax exemption"
    definition_period = YEAR
    reference = (
        # RCW 84.36.381(3)(a)(ii)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        # WAC 458-16A-130
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-130",
    )
