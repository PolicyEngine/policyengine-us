from policyengine_us.model_api import *


class ca_care_electricity(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California CARE electricity discount"
    documentation = "California's CARE program provides this electricity discount to eligible households."
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = "ca_care_eligible"

    def formula(household, period, parameters):
        expense = add(household, period, ["pre_subsidy_electricity_expense"])
        p = parameters(period).gov.states.ca.cpuc.care
        return p.discount * expense
