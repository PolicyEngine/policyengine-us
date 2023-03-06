from policyengine_us.model_api import *


class ca_fera(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California FERA"
    documentation = "California's FERA program provides this electricity discount to eligible households."
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        is_eligible = household("ca_fera_eligible", period)
        amount = household("ca_fera_amount_if_eligible", period)
        return is_eligible * amount
