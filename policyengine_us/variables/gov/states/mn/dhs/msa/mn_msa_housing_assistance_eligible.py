from policyengine_us.model_api import *


class mn_msa_housing_assistance_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Whether the person qualifies for Minnesota Supplemental Aid housing assistance"
    )
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )
