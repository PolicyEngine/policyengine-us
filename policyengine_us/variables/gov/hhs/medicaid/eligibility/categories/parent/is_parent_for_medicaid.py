from policyengine_us.model_api import *


class is_parent_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Parents"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396u-1"

    formula = all_of_variables(
        ["is_parent_for_medicaid_fc", "is_parent_for_medicaid_nfc"]
    )
