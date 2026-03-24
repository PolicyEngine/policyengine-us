from policyengine_us.model_api import *


class pa_philadelphia_wage_tax_resident(Variable):
    value_type = bool
    entity = Person
    label = "Philadelphia wage tax resident status"
    documentation = (
        "Whether this person is treated as a Philadelphia resident for wage "
        "tax purposes."
    )
    definition_period = YEAR
    default_value = False
