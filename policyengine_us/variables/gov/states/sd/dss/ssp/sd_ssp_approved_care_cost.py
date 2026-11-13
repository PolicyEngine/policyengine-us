from policyengine_us.model_api import *


class sd_ssp_approved_care_cost(Variable):
    value_type = float
    entity = Person
    label = "Approved South Dakota SSP care bill for the month"
    definition_period = MONTH
    unit = USD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:04:15"
    documentation = "Actual approved charge for covered days. Required for both care settings; the assisted living schedule additionally caps the payment."
