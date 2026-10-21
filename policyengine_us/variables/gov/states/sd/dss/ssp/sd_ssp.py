from policyengine_us.model_api import *


class sd_ssp(Variable):
    value_type = float
    entity = Person
    label = "South Dakota State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.SD
    reference = (
        "https://sdlegislature.gov/Statutes/28-5A-1",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415011DEN",
        "https://sdlegislature.gov/Rules/Administrative/67:12:14:04",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/sd.html",
    )
    adds = ["sd_ssp_independent", "sd_ssp_care"]
