from policyengine_us.model_api import *


class ca_state_supplement_dependent_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement dependent amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        # Blind amount
        blind = person("is_blind", period)
        is_disabled = person("is_disabled", period)
        age = person("monthly_age", period)
        # Dependent amount
        dependent = person("is_tax_unit_dependent", period)
        dependent_age_eligible = age < p.dependent.age_limit
        dependent_count = spm_unit.sum(
            dependent & dependent_age_eligible & (is_disabled | blind)
        )
        eligible_person = person("ca_state_supplement_eligible_person", period)
        eligible_head_or_spouse_present = spm_unit.any(eligible_person)
        return (
            dependent_count
            * p.dependent.amount
            * eligible_head_or_spouse_present
        )
