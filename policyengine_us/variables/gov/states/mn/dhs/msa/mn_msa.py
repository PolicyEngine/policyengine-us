from policyengine_us.model_api import *


class mn_msa(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota Supplemental Aid"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/256D.44"

    adds = ["mn_msa_person"]
