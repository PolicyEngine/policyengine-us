from policyengine_us.model_api import *


class tx_tanf_demographic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas TANF demographic eligibility"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Must have at least one eligible child
        has_eligible_child = spm_unit.any(
            person("tx_tanf_eligible_child", period)
        )

        # Must have a caretaker (parent or relative)
        has_parent = spm_unit.any(person("is_parent", period))

        # Basic demographic requirement: has eligible child and caretaker
        return has_eligible_child & has_parent
