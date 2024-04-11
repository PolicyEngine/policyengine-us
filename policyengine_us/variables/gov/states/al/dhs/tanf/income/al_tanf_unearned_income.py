from policyengine_us.model_api import *

class al_tanf_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "AL TANF unearned income"
    defined_for = StateCode.AL
    definition_period = MONTHS_IN_YEAR

def formula(person, period, parameters):
        # Calculate the sum of all types of earned income
        veterans_benefits = person('veterans_benefits', period, 0)
        child_support_received = person('child_support_received', period, 0)
        social_security = person('social_security', period, 0)
        unemployment_compensation = person('unemployment_compensation', period, 0)
        # Calculate the sum of unremunerated income
        total_unearned_income = veterans_benefits + child_support_received + social_security + unemployment_compensation

        return total_unearned_income