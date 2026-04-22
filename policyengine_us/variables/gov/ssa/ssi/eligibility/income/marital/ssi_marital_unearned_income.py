from policyengine_us.model_api import *


class ssi_marital_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Total SSI unearned income for a marital unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        couple_computation = person("ssi_couple_computation_applies", period)
        unearned_income = person("ssi_unearned_income", period)

        return where(
            couple_computation,
            person.marital_unit.sum(unearned_income),
            unearned_income,
        )
