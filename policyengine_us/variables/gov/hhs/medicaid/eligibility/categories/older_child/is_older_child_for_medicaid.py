from policyengine_us.model_api import *


class is_older_child_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Older children"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_D"

    formula = all_of_variables(
        ["is_older_child_for_medicaid_fc", "is_older_child_for_medicaid_nfc"]
    )
