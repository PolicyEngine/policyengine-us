from policyengine_us.model_api import *


class months_receiving_social_security_disability(Variable):
    value_type = int
    entity = Person
    label = "Number of months person has received social security disability"
    definition_period = YEAR
