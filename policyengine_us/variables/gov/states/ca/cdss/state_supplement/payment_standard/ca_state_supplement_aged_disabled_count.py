from policyengine_us.model_api import *


class ca_state_supplement_aged_disabled_count(Variable):
    value_type = int
    entity = SPMUnit
    label = "California SSI state supplement aged or disabled count"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Aged or disabled amount
        is_disabled = person("is_disabled", period)
        age = person("monthly_age", period)
        is_aged = age >= p.aged_or_disabled.age_threshold
        aged_or_disabled = (is_aged | is_disabled) * head_or_spouse
        return spm_unit.sum(aged_or_disabled)
