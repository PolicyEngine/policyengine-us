from policyengine_us.model_api import *


class ms_ccpp_minimum_fee_category(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Mississippi CCPP minimum-fee category"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=41"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.eligibility
        person = spm_unit.members
        has_protective_child = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        has_ssi_disabled_parent = spm_unit.any(
            is_head_or_spouse
            & person("is_ssi_disabled", period.this_year)
            & ((person("ssi", period) > 0) | person("receives_ssi", period))
        )
        age = person("age", period.this_year)
        has_special_needs_child = spm_unit.any(
            person("is_tax_unit_dependent", period.this_year)
            & person("is_disabled", period.this_year)
            & (age < p.special_needs_child_age_limit)
        )
        return has_protective_child | has_ssi_disabled_parent | has_special_needs_child
