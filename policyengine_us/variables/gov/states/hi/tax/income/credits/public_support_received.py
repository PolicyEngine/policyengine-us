from policyengine_us.model_api import *


class public_support_received(Variable):
    value_type = bool
    entity = Person
    label = "child received public support or not"
    definition_period = YEAR
    defined_for = StateCode.HI
