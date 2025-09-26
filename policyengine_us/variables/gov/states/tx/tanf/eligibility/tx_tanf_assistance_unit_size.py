from policyengine_us.model_api import *


class tx_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Texas TANF assistance unit size"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("tx_tanf_eligible_child", period)
        is_parent = person("is_parent", period)

        # Count eligible children and parents
        eligible_children = spm_unit.sum(eligible_child)
        parents = spm_unit.sum(is_parent)

        return eligible_children + parents
