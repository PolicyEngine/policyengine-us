from policyengine_us.model_api import *


class wa_pte_retired_due_to_disability(Variable):
    value_type = bool
    entity = Person
    label = "Retired from regular gainful employment by reason of disability for the Washington senior and disabled persons property tax exemption"
    documentation = (
        "At the time of filing, retired from regular gainful employment by "
        "reason of a disability as defined in RCW 84.36.383 (42 U.S.C. "
        "423(d)(1)(A): unable to engage in any substantial gainful activity "
        "because of a medically determinable impairment expected to result in "
        "death or to last at least 12 months). By default a person receiving "
        "Social Security disability insurance benefits qualifies: an award is "
        "the Social Security Administration's finding of disability under that "
        "same definition. Set this to override the default, for example for a "
        "person disabled under the definition who receives no award."
    )
    definition_period = YEAR
    reference = (
        # RCW 84.36.381(3)(a)(i)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        # RCW 84.36.383(6)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
        # WAC 458-16A-130
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-130",
    )

    def formula(person, period, parameters):
        return person("social_security_disability", period) > 0
