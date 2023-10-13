from policyengine_us.model_api import *


class mt_disability_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana disability income subtraction"
    defined_for = StateCode.MT
    unit = USD
    definition_period = YEAR
    reference = "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.mt.tax.income.subtractions.disability_income
        age_eligible = person("age", period) < p.age_threshold
        is_head = person("is_tax_unit_head", period)
        age_eligible_head = age_eligible & is_head
        is_spouse = person("is_tax_unit_spouse", period)
        age_eligible_spouse = age_eligible & is_spouse
        is_retired = person("is_retired", period)
        retired_head = age_eligible_head & is_retired
        retired_spouse = age_eligible_spouse & is_retired
        is_disabled = person("is_disabled", period)
        qualified_head = retired_head & is_disabled
        qualified_spouse = retired_spouse & is_disabled
        qualified_head_or_spouse = qualified_head | qualified_spouse
        eligible_benefits = (
            person("disability_benefits", period) * qualified_head_or_spouse
        )
        return tax_unit.sum(eligible_benefits)
