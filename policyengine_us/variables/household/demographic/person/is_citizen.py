from policyengine_us.model_api import *


class is_citizen(Variable):
    value_type = bool
    entity = Person
    label = "Is a U.S. citizen (see has_itin, has_daca_tps_status, has_undocumented_status for non-citizen status)"
    definition_period = YEAR
    default_value = True
