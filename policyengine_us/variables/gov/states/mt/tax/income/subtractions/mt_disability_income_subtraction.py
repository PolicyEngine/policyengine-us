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
        # select those who are retired on total disability and disabled, and
        # calculate the corresbonding disability benefits.
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.mt.tax.income.subtractions.disability_income
        age_eligible = person("age", period) < p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_retired_on_disability = person(
            "retired_on_total_disability", period
        )
        retired = age_eligible & is_retired_on_disability
        is_disabled = person("is_disabled", period)
        retired_disabled = retired & is_disabled
        qualified_head_or_spouse = retired_disabled & head_or_spouse
        eligible_benefits = (
            person("disability_benefits", period) * qualified_head_or_spouse
        )
        return tax_unit.sum(eligible_benefits)
