from policyengine_us.model_api import *


class ma_eaedc_eligible_disabled_head_or_spouse(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Disabled head or spouse present for Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010"  # (B)

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_disabled = person("is_disabled", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        ssi_eligible = person("is_ssi_eligible", period)
        return spm_unit.any(is_disabled & head_or_spouse & ~ssi_eligible)
