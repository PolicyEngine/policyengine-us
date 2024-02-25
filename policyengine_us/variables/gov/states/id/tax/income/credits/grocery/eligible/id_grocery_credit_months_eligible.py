from policyengine_us.model_api import *

class id_grocery_credit_months_eligible_prorated(Variable):
    value_type = float
    entity = Person
    label = "Eligible for the Idaho grocery credit"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        eligible_months_sum = 0
        year = period.start.year  
        for month in range(1, 13):
            monthly_period_str = f"{year}-{month:02d}"
            eligible_months_sum += person('id_grocery_credit_eligible', monthly_period_str)
        return eligible_months_sum / MONTHS_IN_YEAR
