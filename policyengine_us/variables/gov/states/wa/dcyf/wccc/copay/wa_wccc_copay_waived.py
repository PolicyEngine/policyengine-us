from policyengine_us.model_api import *


class wa_wccc_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington WCCC copayment is waived"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0075"

    def formula(spm_unit, period, parameters):
        teen_age_limit = parameters(
            period
        ).gov.states.wa.dcyf.wccc.eligibility.age_threshold.teen_parent
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        age = person("age", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        is_teen_parent = is_head_or_spouse & (age < teen_age_limit) & is_in_school
        any_teen_parent = spm_unit.sum(is_teen_parent) > 0
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return any_teen_parent | is_homeless
