from policyengine_us.model_api import *


class ssi_marital_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Total SSI earned income for a marital unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        both_eligible = person("ssi_marital_both_eligible", period)
        earned_income = person("ssi_earned_income", period)

        return where(
            both_eligible,
            person.marital_unit.sum(earned_income),
            earned_income,
        )
