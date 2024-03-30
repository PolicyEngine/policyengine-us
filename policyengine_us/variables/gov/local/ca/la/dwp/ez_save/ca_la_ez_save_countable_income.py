from policyengine_us.model_api import *


class ca_la_ez_save_countable_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Los Angeles County EZ Save program countable income"
    defined_for = "in_la"

    adds = "gov.local.ca.la.dwp.ez_save.income_sources"
