from policyengine_us.model_api import *


class wi_retirement_income_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Wisconsin retirement income exclusion"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        person = tax_unit.members
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age_eligible = (age >= p.min_age) * head_or_spouse
        return tax_unit.any(age_eligible)
