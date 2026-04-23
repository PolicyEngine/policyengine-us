from policyengine_us.model_api import *


class in_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Indiana State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501401001CHI",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/in.html",
    )

    def formula(person, period, parameters):
        sapn_eligible = person("in_ssp_sapn_eligible", period)
        rcap_eligible = person("in_ssp_rcap_eligible", period)
        return sapn_eligible | rcap_eligible
