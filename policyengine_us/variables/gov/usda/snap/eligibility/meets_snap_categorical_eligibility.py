from policyengine_us.model_api import *


class meets_snap_categorical_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SNAP categorical eligibility"
    documentation = "Whether this SPM unit is eligible for SNAP benefits via participation in other programs"
    definition_period = MONTH
    reference = "https://fns-prod.azureedge.net/sites/default/files/resource-files/fna-2008-amended-through-pl-116-94.pdf#page=11"

    def formula(spm_unit, period, parameters):
        programs = parameters(period).gov.usda.snap.categorical_eligibility
        return add(spm_unit, period, programs) > 0
