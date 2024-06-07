from policyengine_us.model_api import *


class mt_disability_income_exclusion_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Montana disability income exclusion eligible person"
    defined_for = StateCode.MT
    definition_period = YEAR
    reference = "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217"

    def formula(person, period, parameters):
        # first select head and spouse with ages below the specific threshold, and
        # select those who are retired on total disability and disabled.
        p = parameters(
            period
        ).gov.states.mt.tax.income.subtractions.disability_income
        age_eligible = person("age", period) < p.age_threshold
        is_retired_on_disability = person(
            "retired_on_total_disability", period
        )
        eligible_retiree = age_eligible & is_retired_on_disability
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_retiree & head_or_spouse
