from policyengine_us.model_api import *


class ct_ssp_lives_with_others(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person lives with unrelated persons in the community under Connecticut SSP"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html"
