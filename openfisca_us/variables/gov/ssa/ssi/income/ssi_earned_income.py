from openfisca_us.model_api import *


class ssi_earned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income"
    definition_period = YEAR

    def formula(person, period, parameters):
        add(
            person,
            period,
            [
                "ssi_personal_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
