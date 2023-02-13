from policyengine_us.model_api import *


class ca_care_poverty_line(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Poverty line as defined for California CARE program"
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    def formula(household, period, parameters):
        n = household("household_size", period)
        # CARE treats one-person households as two-person households.
        adj_n = max_(n, 2)
        state_group = household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (adj_nadj_n - 1)
