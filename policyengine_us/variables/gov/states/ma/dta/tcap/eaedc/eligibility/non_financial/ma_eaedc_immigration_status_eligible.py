from policyengine_us.model_api import *


class ma_eaedc_immigration_status_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC based on immigration status"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-440"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        immigration_status = person("immigration_status", period)
        is_undocumented = (
            immigration_status
            == immigration_status.possible_values.UNDOCUMENTED
        )
        return spm_unit.any(head_or_spouse & ~is_undocumented)
