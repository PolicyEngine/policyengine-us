from policyengine_us.model_api import *


class is_optional_senior_or_disabled_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Income-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities"
    documentation = (
        "True if the tax unit’s countable income—after the state-specific "
        "income disregard—is below the income limit that the state sets for its "
        "optional pathway for aged, blind, or disabled individuals who are not "
        "otherwise SSI-eligible."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        # income & assets
        personal_income = person("ssi_countable_income", period)  # $/year
        tax_unit = person.tax_unit
        income = tax_unit.sum(personal_income)

        #  Flags & state info
        is_joint = tax_unit("tax_unit_is_joint", period)
        state = person.household("state_code_str", period)

        #  Parameters ─
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        # Monthly disregard
        monthly_income_disregard = where(
            is_joint,
            p.income.disregard.couple[state],
            p.income.disregard.individual[state],
        )

        # Annualize
        income_disregard = monthly_income_disregard * MONTHS_IN_YEAR

        #  Poverty-guideline-based income limit
        limit_pct = where(
            is_joint,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        fpg_annual = tax_unit("tax_unit_fpg", period)
        income_limit = limit_pct * fpg_annual

        #  Income test
        countable_income = income - income_disregard
        return countable_income < income_limit
