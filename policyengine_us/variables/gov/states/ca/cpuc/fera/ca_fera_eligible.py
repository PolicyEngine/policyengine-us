from policyengine_us.model_api import *


class ca_fera_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California FERA program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.12"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        # Check not eligible for CARE
        care_eligible = household("ca_care_eligible", period)
        # Check at least 3 people in household
        n = household("household_size", period)
        n_eligible = n >= 3
        # Check income eligibility with respect to percent of the poverty line.
        # Must be above 200% of the poverty line (CARE requirements), but less than or equal to 250% of the poverty line.
        income = household("ca_household_income", period)
        ca_care_poverty_line = household("ca_care_poverty_line", period)
        p = parameters(period).gov.states.ca.cpuc
        care_fpl_limit = p.care.eligibility.fpl_limit
        fera_fpl_limit = p.fera.eligibility.fpl_limit
        income_eligible = (income <= (ca_care_poverty_line * fera_fpl_limit)) and (income > (ca_care_poverty_line * care_fpl_limit))
        return income_eligible and n_eligible and not care_eligible
