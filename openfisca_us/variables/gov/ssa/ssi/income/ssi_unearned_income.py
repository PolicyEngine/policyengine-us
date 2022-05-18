from openfisca_us.model_api import *


class ssi_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income"
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "ssi_personal_unearned_income",
            "ssi_unearned_income_deemed_from_ineligible_spouse",
        ]
    )
