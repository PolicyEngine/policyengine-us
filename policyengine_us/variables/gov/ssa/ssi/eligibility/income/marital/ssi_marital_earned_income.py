from policyengine_us.model_api import *


class ssi_marital_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Total SSI earned income for a marital unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        couple_computation = person("ssi_couple_computation_applies", period)
        earned_income = person("ssi_earned_income", period)

        return where(
            couple_computation,
            person.marital_unit.sum(earned_income),
            earned_income,
        )
