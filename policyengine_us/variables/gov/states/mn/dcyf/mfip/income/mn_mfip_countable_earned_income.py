from policyengine_us.model_api import *


class mn_mfip_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.03#stat.256P.03.2",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001818",
    )
    defined_for = StateCode.MN
    adds = ["mn_mfip_countable_earned_income_person"]
