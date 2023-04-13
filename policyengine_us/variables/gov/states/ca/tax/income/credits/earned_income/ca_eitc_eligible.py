from policyengine_us.model_api import *


class ca_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "CalEITC eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income

        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)

        meets_age_requirements = tax_unit.any(
            (age >= p.eligibility.age.min)
            & (age <= p.eligibility.age.max)
            & ~is_dependent
        )

        eitc_investment_income = tax_unit(
            "eitc_relevant_investment_income", period
        )

        meets_investment_income_requirements = (
            eitc_investment_income <= p.eligibility.max_investment_income
        )

        return meets_age_requirements & meets_investment_income_requirements
