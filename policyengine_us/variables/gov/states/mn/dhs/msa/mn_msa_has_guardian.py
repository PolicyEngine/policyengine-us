from policyengine_us.model_api import *


class mn_msa_has_guardian(Variable):
    value_type = bool
    entity = Person
    label = "Whether the person has a court-appointed guardian or conservator under Minnesota Supplemental Aid"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mn.html",
    )
