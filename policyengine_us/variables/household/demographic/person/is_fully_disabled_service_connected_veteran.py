from policyengine_us.model_api import *


class is_fully_disabled_service_connected_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Is a fully disabled veteran who became so as a result of an injury during service"
    definition_period = YEAR
    # True when the Department of Veterans Affairs rates or pays a
    # service-connected disability at the 100% rate, temporary or permanent,
    # including a total rating based on individual unemployability. A
    # permanent rating is is_permanently_disabled_veteran. The model has no
    # input for ratings below 100%.
    reference = (
        "https://www.law.cornell.edu/uscode/text/38/1155",
        "https://www.law.cornell.edu/cfr/text/38/3.340",
        "https://www.law.cornell.edu/cfr/text/38/4.16",
    )
