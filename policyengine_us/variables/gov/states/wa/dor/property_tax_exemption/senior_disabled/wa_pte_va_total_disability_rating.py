from policyengine_us.model_api import *


class wa_pte_va_total_disability_rating(Variable):
    value_type = bool
    entity = Person
    label = "Has a VA total disability rating for a service-connected disability for the Washington senior and disabled persons property tax exemption"
    documentation = "A total disability rating from the U.S. Department of Veterans Affairs for a service-connected disability, without regard to evaluation percent (for example, individual unemployability). By default a fully disabled service-connected veteran (is_fully_disabled_service_connected_veteran) has one. Set this to override the default."
    definition_period = YEAR
    reference = (
        # RCW 84.36.381(3)(a)(ii)(B)
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        # 38 CFR 3.340(a)(2)
        "https://www.law.cornell.edu/cfr/text/38/3.340",
    )

    def formula(person, period, parameters):
        return person("is_fully_disabled_service_connected_veteran", period)
