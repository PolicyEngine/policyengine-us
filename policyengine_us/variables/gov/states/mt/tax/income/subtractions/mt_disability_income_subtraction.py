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
        # first select head and spouse with ages below the specific threshold, and
        # select those who are retired on total disability and disabiled, and
        # calculate the corresbonding disability benefits.
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.mt.tax.income.subtractions.disability_income
        age_eligible_head = tax_unit("age_head", period) < p.age_threshold
        age_eligible_spouse = tax_unit("age_spouse", period) < p.age_threshold
        is_retired_on_disability = person(
            "retired_on_total_disability", period
        )
        retired_head = age_eligible_head & is_retired_on_disability
        retired_spouse = age_eligible_spouse & is_retired_on_disability
        is_disabled = person("is_disabled", period)
        qualified_head = retired_head & is_disabled
        qualified_spouse = retired_spouse & is_disabled
        qualified_head_or_spouse = qualified_head | qualified_spouse
        eligible_benefits = (
            person("disability_benefits", period) * qualified_head_or_spouse
        )
        return tax_unit.sum(eligible_benefits)
