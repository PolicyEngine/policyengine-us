from policyengine_us.model_api import *


class ca_riv_general_relief_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Riverside County General Relief countable income per person"
    definition_period = YEAR
    defined_for = "in_riv"

    adds = "gov.local.ca.riv.general_relief.countable_income.sources"
