from policyengine_us.model_api import *


class total_disability_payments(Variable):
    value_type = float
    entity = Person
    label = "Disability (total) payments"
    unit = USD
    documentation = "Wages (or payments in lieu thereof) paid to an individual for permanent and total disability"
    definition_period = YEAR
