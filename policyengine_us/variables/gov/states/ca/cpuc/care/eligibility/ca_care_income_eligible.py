from policyengine_us.model_api import *


class ca_care_income_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        # Check income eligibility with respect to percent of the poverty line.
        income = household("household_market_income", period)
        p = parameters(period).gov.states.ca.cpuc.care.eligibility
        # Calculate income limit based on federal poverty line, adjusted to
        # set one-person households as two-person.
        poverty_line = household("ca_care_poverty_line", period)
        return income <= (poverty_line * p.fpl_limit)
