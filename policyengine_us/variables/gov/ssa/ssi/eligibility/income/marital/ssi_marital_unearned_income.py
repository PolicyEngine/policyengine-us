from policyengine_us.model_api import *


class ssi_marital_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Total SSI unearned income for a marital unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        both_eligible = person("ssi_marital_both_eligible", period)
        unearned_income = person("ssi_unearned_income", period)

        return where(
            both_eligible,
            person.marital_unit.sum(unearned_income),
            unearned_income,
        )
