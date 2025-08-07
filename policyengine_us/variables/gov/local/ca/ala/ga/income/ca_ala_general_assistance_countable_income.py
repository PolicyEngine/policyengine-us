from policyengine_us.model_api import *


class ca_ala_general_assistance_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Eligible for Alameda County General Assistance based on age requirements"
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    adds = ["ca_ala_general_assistance_countable_income_person"]
