from policyengine_us.model_api import *


class co_greenwood_village_employee_occupational_privilege_tax_months(Variable):
    value_type = int
    entity = Person
    label = "Greenwood Village employee occupational privilege taxable months"
    documentation = (
        "Number of months this person is subject to Greenwood Village's "
        "employee occupational privilege tax."
    )
    definition_period = YEAR
    default_value = 0
