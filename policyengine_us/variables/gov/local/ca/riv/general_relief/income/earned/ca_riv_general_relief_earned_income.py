from policyengine_us.model_api import *


class ca_riv_general_relief_earned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Riverside County General Relief earned income per person"
    definition_period = MONTH
    defined_for = "in_riv"

    adds = "gov.local.ca.riv.general_relief.income.sources.earned"
