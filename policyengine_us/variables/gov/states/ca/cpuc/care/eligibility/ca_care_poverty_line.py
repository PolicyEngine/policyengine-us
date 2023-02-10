from policyengine_us.model_api import *


class ca_care_poverty_line(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Poverty line as defined for California CARE program"
    reference = "https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program"
    defined_for = StateCode.CA

    # # capped_size = max_(size, 2)