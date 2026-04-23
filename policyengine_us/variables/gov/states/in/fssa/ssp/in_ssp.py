from policyengine_us.model_api import *


class in_ssp(Variable):
    value_type = float
    entity = Person
    label = "Indiana State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "in_ssp_eligible"
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501401001CHI",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/in.html",
    )
    adds = ["in_ssp_sapn", "in_ssp_rcap"]
