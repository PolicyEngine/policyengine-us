from openfisca_us.model_api import *


class is_pregnant_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant people"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_A"

    formula = all_of_variables(
        ["is_pregnant_for_medicaid_fc", "is_pregnant_for_medicaid_nfc"]
    )
