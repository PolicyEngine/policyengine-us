from policyengine_us.model_api import *


class ca_eitc_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California foster youth tax credit"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income
        tax_unit = person.tax_unit
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)

        eitc_investment_income = tax_unit(
            "eitc_relevant_investment_income", period
        )
        age_eligible = (age >= p.eligibility.age.min) & (
            age <= p.eligibility.age.max
        )
        investment_income_eligible = (
            eitc_investment_income <= p.eligibility.max_investment_income
        )
        return age_eligible & ~is_dependent & investment_income_eligible
