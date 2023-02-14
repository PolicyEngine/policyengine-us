from policyengine_us.model_api import *


class ca_care_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        # Check income eligibility with respect to percent of the poverty line.
        income = household("household_income", period)
        p = parameters(period).gov.states.ca.cpuc.care.eligibility
        # Calculate income limit based on federal poverty line.
        size = household("household_size", period)
        # Recreate the poverty line for the adjusted-size household.
        # # Treat one-person households as two-person.
        # capped_size = max_(size, 2)
        income_eligible = income <= p.income_threshold
        # Check categorical eligibility.
        is_categorically_eligible = add(household, period, p.categorical) > 0
        # Return True if either income or categorical eligibility is met.
        return income_eligible | is_categorically_eligible
