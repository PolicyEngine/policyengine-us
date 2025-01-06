from policyengine_us.model_api import *

class or_liheap_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income threshold for Oregon LIHEAP eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#Pg=55"

    defined_for = StateCode.OR
