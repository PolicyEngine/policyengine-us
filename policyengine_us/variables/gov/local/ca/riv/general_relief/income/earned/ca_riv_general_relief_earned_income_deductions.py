from policyengine_us.model_api import *


class ca_riv_general_relief_earned_income_deductions(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Riverside County General Relief earned income deductions"
    definition_period = MONTH
    defined_for = "in_riv"

    adds = "gov.local.ca.riv.general_relief.income.deductions.sources"
