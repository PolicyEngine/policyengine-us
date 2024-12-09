from policyengine_us.model_api import *


class has_a_vehicle_loan(Variable):
    value_type = bool
    entity = Person
    label = "Has vehicel loan or lease"
    definition_period = YEAR

    def formula(person, period, parameters):
        total_mortage_expenses = person("vehicle_mortgage_expense",period)  
        return total_mortage_expenses > 0 
