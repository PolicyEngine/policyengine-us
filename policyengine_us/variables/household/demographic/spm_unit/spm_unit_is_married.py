from policyengine_us.model_api import *


class spm_unit_is_married(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM unit is married"
    documentation = "Whether the adults in this SPM unit are married."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        return spm_unit.any(person("is_tax_unit_spouse", period))
