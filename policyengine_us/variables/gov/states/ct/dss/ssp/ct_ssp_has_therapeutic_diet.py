from policyengine_us.model_api import *


class ct_ssp_has_therapeutic_diet(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person requires a therapeutic diet under Connecticut SSP"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html"
