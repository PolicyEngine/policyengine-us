from policyengine_us.model_api import *


class is_migratory_child(Variable):
    value_type = bool
    entity = Person
    label = "Is migratory child"
    documentation = "Whether a child made a qualifying move in the last 36 months as, with, or to join a migratory agricultural worker or fisher"
    definition_period = YEAR
