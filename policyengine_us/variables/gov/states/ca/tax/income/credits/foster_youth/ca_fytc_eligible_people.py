from policyengine_us.model_api import *


class ca_fytc_eligible_people(Variable):
    value_type = int
    entity = TaxUnit
    label = "FYTC Eligible"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"

    adds = ["ca_fytc_eligible"]

#TODO: create a ca_foster_care.py -> empty bool | person level 