from policyengine_us.model_api import *


class ca_fera_amount_if_eligible(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California FERA discounted amount"
    documentation = "California's CARE program provides this electricity discount to eligible households."
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        expense = add(household, period, ["electricity_expense"])
        p = parameters(period).gov.states.ca.cpuc.fera
        return p.discount * expense
