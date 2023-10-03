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
        is_under_age = person("age", period) < p.age
        is_head = person("is_tax_unit_head", period)
        underage_head = is_under_age & is_head
        is_spouse = person("is_tax_unit_spouse", period)
        underage_spouse = is_under_age & is_spouse
        is_retired = person("is_retired", period)
        retired_head = underage_head & is_retired
        retired_spouse = underage_spouse & is_retired
        is_disabled = person("is_permanently_and_totally_disabled", period)
        qualified_head = retired_head & is_disabled
        qualified_spouse = retired_spouse & is_disabled
        is_head_or_spouse = qualified_head | qualified_spouse
        return tax_unit.sum(
            person("disability_benefits", period) * is_head_or_spouse
        )
