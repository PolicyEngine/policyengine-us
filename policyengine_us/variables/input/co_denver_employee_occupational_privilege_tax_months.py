from policyengine_us.model_api import *


class co_denver_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Denver employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Denver's employee "
        "occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0
