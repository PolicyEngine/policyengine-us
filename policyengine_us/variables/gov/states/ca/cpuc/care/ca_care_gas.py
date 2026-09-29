from policyengine_us.model_api import *


class ca_care_gas(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = USD
    label = "California CARE gas discount"
    documentation = (
        "California's CARE program discounts natural gas bills for eligible "
        "households, separately from its electricity discount. The model treats "
        "gas_expense as the bill before the discount and applies the rate to the "
        "whole bill; the tariffs discount customer, commodity, and transportation "
        "charges, which make up nearly all of it. The model has no "
        "utility-territory input, so it applies the discount to every eligible "
        "California household with a gas expense."
    )
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = "ca_care_eligible"

    def formula(household, period, parameters):
        expense = add(household, period, ["gas_expense"])
        p = parameters(period).gov.states.ca.cpuc.care
        return p.gas_discount * expense
