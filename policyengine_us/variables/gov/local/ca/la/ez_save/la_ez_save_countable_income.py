from policyengine_us.model_api import *


class la_ez_save_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Los Angeles County EZ Save program countable income"
    defined_for = "in_la"

    adds = "gov.local.ca.la.ez_save.income_sources"
