from policyengine_us.model_api import *


class is_adult_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Working-age and childless adults"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII"
    )

    formula = all_of_variables(
        ["is_adult_for_medicaid_fc", "is_adult_for_medicaid_nfc"]
    )
