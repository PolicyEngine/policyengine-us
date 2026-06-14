from policyengine_us.model_api import *


class ca_cc_general_assistance_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Contra Costa County General Assistance countable income"
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    adds = ["ca_cc_general_assistance_countable_income_person"]
