from policyengine_us.model_api import *


class public_support_received(Variable):
    value_type = bool
    entity = Person
    label = "Child receiving public support"
    definition_period = YEAR
