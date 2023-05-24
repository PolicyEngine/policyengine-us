from policyengine_us.model_api import *


class mt_qualifying_child_amount(Variable):
    value_type = int
    entity = TaxUnit
    label = "CalEITC eligible children amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.eitc

        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)

        meets_requirements_amount = tax_unit.sum(
            (person("mt_is_qualifying_child_for_eitc", period) == True)
            & ~is_dependent
        )

        eitc_investment_income = tax_unit(
            "eitc_relevant_investment_income", period
        )

        meets_investment_income_requirements = (
            eitc_investment_income <= p.eligibility.max_investment_income
        )

        return meets_age_requirements & meets_investment_income_requirements