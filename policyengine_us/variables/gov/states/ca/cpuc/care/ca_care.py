from policyengine_us.model_api import *


class ca_care(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California CARE"
    documentation = "California's CARE program provides this electricity discount to eligible households."
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = "ca_care_eligible"

    def formula(household, period, parameters):
        is_eligible = household("ca_care_eligible", period)
        amount = household("ca_care_amount_if_eligible", period)
        return is_eligible * amount
