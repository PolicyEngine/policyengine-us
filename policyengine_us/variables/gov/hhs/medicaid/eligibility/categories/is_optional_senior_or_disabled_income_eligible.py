from policyengine_us.model_api import *


class is_optional_senior_or_disabled_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Income eligibility for a state's optional Medicaid pathway for seniors "
        "or people with disabilities"
    )
    documentation = (
        "True if the tax unit's countable income after the state-specific "
        "income disregard is below the income limit that the state sets for its "
        "optional pathway for aged, blind, or disabled individuals who are not "
        "otherwise SSI-eligible."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        personal_income = person(
            "medicaid_optional_senior_or_disabled_countable_income", period
        )
        tax_unit = person.tax_unit
        income = tax_unit.sum(personal_income)

        is_joint = tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        limit_pct = where(
            is_joint,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        fpg_annual = tax_unit("tax_unit_fpg", period)
        income_limit = limit_pct * fpg_annual

        return income < income_limit
