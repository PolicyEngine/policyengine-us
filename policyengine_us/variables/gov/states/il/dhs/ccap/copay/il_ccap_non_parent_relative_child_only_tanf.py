from policyengine_us.model_api import *


class il_ccap_non_parent_relative_child_only_tanf(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP non-parent relative child-only TANF copay exemption"
    documentation = "Whether a non-parent relative receives child-only TANF and needs child care because of the relative's employment."
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=54862"
