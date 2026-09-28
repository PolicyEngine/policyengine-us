from policyengine_us.model_api import *


class mn_mfip_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota MFIP gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_00171203"
    defined_for = StateCode.MN

    adds = "gov.states.mn.dcyf.mfip.income.sources.unearned"
