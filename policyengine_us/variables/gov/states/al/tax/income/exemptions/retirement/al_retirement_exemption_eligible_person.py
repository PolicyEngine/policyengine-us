from policyengine_us.model_api import *


class al_retirement_exemption_eligible_person(Variable):
    value_type = float
    entity = Person
    label = "Alabama retirement exemption"
    unit = USD
    # The Code of Alabama Section 40-18-19 (a)(13).
    documentation = "https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        age = person("age", period)
        pension_income = person("taxable_pension_income", period)
        eligible_age = age >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return min_(
            pension_income * eligible_age * head_or_spouse, p.max_amount
        )
