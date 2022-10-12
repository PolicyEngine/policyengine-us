from policyengine_us.model_api import *


class is_young_adult_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Young adults"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396d#a_i"

    formula = all_of_variables(
        ["is_young_adult_for_medicaid_fc", "is_young_adult_for_medicaid_nfc"]
    )
