from policyengine_us.model_api import *


class casualty_loss(Variable):
    value_type = float
    entity = Person
    label = "Casualty/theft loss"
    documentation = (
        "Puerto Rico's casualty loss deductions do not use this amount. They "
        "use pr_principal_residence_casualty_loss and "
        "pr_personal_property_casualty_loss instead."
    )
    unit = USD
    definition_period = YEAR
