from policyengine_us.model_api import *


class co_ccap_children_in_care(Variable):
    value_type = int
    entity = SPMUnit
    label = (
        "Number of children in care under the Colorado Child Care Assistance Program"
    )
    reference = (
        # PDF pages 79, 84
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=79",
    )
    definition_period = MONTH
    defined_for = StateCode.CO
    adds = ["co_ccap_child_in_care"]
