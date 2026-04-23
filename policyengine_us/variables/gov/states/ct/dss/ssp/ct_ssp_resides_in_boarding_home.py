from policyengine_us.model_api import *


class ct_ssp_resides_in_boarding_home(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person resides in a licensed room and board facility under Connecticut SSP"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html"
