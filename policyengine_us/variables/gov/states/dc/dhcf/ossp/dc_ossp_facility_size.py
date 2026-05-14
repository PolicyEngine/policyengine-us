from policyengine_us.model_api import *


class dc_ossp_facility_size(Variable):
    value_type = int
    entity = Person
    label = "Number of beds in the adult foster care home"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49"
