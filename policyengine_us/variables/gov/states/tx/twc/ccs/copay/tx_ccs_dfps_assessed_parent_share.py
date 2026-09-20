from policyengine_us.model_api import *


class tx_ccs_dfps_assessed_parent_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.TX
    label = "Texas DFPS-assessed monthly parent share of child-care cost"
    documentation = (
        "Parent share specifically assessed by DFPS for protective-services "
        "child care. Under 40 TAC 809.19(a)(3)(D), parents are exempt unless "
        "DFPS assesses a share. Defaults to zero."
    )
    reference = "https://www.twc.texas.gov/sites/default/files/ogc/docs/rules-chapter-809-child-care-services-twc.pdf#page=19"
