from policyengine_us.model_api import *


class il_ccap_child_care_worker(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Illinois CCAP qualifying child care worker"
    documentation = "Whether a parent or guardian works for a qualifying child care provider and spends at least 75 percent of regular daily work serving early childhood education and care."
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=54862"
