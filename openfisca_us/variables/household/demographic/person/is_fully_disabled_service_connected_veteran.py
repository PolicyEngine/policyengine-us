from openfisca_us.model_api import *


class is_fully_disabled_service_connected_veteran(Variable):
    value_type = bool
    entity = Person
    label = "Is a fully disabled veteran who became so as a result of an injury during service"
    definition_period = YEAR
    question = (
        "Are you fully disabled due to an injury during military service?"
    )
