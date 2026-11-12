from policyengine_us.model_api import *


class is_permanently_disabled_veteran(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Permanently disabled veteran"
    # True when the Department of Veterans Affairs has rated the veteran's
    # disability permanent and total, for service-connected compensation or
    # for a pension, which requires a permanent and total non-service-connected
    # disability (38 U.S.C. 1521(a)). A 100% service-connected rating that is
    # not permanent is is_fully_disabled_service_connected_veteran.
    reference = (
        "https://www.law.cornell.edu/cfr/text/38/3.340",
        "https://www.law.cornell.edu/uscode/text/38/1521",
    )
