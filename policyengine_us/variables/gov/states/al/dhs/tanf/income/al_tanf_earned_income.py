from policyengine_us.model_api import *

class al_tanf_earned_income(Variable):
    value_type = float
    entity = Person
    label = "AL TANF earned income "
    defined_for = StateCode.AL
    definition_period = MONTHS_IN_YEAR

    def formula(person, period, parameters):
        # Calculate the sum of all types of earned income
        employment_income = person('employment_income', period, 0)
        self_employment_income = person('self_employment_income', period, 0)
        earned_income_tax_credit = person('earned_income_tax_credit', period, 0)
        # Calculate the sum of unremunerated income
        total_earned_income = employment_income + self_employment_income + earned_income_tax_credit

        return total_earned_income


