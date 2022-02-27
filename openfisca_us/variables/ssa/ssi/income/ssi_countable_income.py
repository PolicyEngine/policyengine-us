from openfisca_us.model_api import *


class ssi_countable_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income countable income"
    label = "SSI countable income"
    unit = USD

    def formula(person, period, parameters):
        # TODO: Add deductions.
        return add(
            person,
            period,
            ["ssi_earned_income", "ssi_unearned_income", "ssi_deemed_income"],
        )
