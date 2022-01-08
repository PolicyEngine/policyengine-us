from openfisca_us.model_api import *


class receives_or_needs_protective_services(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Child receiving or needs protective services"
