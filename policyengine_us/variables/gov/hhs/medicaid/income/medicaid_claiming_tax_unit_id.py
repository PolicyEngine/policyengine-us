from policyengine_us.model_api import *


class medicaid_claiming_tax_unit_id(Variable):
    value_type = int
    entity = Person
    label = "Tax unit ID claiming this person for Medicaid MAGI household rules"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"
    default_value = 0
    documentation = (
        "Optional identifier for the tax unit expected to claim this person as "
        "a dependent. A value of 0 means no known claiming tax unit."
    )
