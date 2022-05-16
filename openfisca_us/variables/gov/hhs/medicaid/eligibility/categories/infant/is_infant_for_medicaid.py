from openfisca_us.model_api import *


class is_infant_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Infants"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_B"

    formula = all_of_variables(
        ["is_infant_for_medicaid_fc", "is_infant_for_medicaid_nfc"]
    )
