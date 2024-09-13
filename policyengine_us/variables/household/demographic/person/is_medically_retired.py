from policyengine_us.model_api import *


class is_medically_retired(Variable):
    value_type = bool
    entity = Person
    label = "Is medically retired"
    definition_period = YEAR
    documentation = "Retirement caused by a person’s inability to work due to poor health or a disabling physical injury."
