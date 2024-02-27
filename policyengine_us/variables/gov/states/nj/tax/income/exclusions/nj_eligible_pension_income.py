from policyengine_us.model_api import *


class nj_eligible_pension_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey pension income eligible for pension exclusion"
    unit = USD
    documentation = "New Jersey pension income eligible for pension exclusion"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-10/",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        is_blind = person("is_blind", period)
        is_disabled = person("is_disabled", period)
        age_eligible = person("age", period) >= p.age_threshold
        demographic_eligible = age_eligible | is_blind | is_disabled

        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        role_eligible = is_head | is_spouse

        eligible = demographic_eligible & role_eligible
        return eligible * person("taxable_pension_income", period)
