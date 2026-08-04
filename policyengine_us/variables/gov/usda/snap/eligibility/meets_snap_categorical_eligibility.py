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
        spm_level_programs = [program for program in programs if program != "ssi"]
        person = spm_unit.members
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        all_members_receive_ssi = spm_unit.all(receives_ssi)
        return (
            all_members_receive_ssi
            | (add(spm_unit, period, spm_level_programs) > 0)
            | spm_unit("receives_tanf", period)
        )
