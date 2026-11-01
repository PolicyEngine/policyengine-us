from policyengine_us.model_api import *


class is_optional_senior_or_disabled_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Income eligibility for a state's optional Medicaid pathway for seniors "
        "or people with disabilities"
    )
    documentation = (
        "True if the countable income of the individual, or of the married "
        "couple living together, after the state-specific "
        "income disregard does not exceed the income limit that the state sets "
        "for its optional pathway for aged, blind, or disabled individuals who "
        "are not otherwise SSI-eligible. The limits are income maxima, so "
        "income exactly equal to the limit qualifies, except in states whose "
        "rules require income below the limit (Oregon)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0250.pdf#page=1",
    )

    def formula(person, period, parameters):
        personal_income = person(
            "medicaid_optional_senior_or_disabled_countable_income", period
        )
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, not the tax filing unit.
        income = person.marital_unit.sum(personal_income)
        income_limit = person(
            "medicaid_optional_senior_or_disabled_income_limit", period
        )
        # Most states cover income at or below the limit; Oregon requires
        # adjusted income "below the standard" (OAR 461-155-0250(3)).
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.limit
        below_only = p.requires_income_below_limit[state].astype(bool)
        return where(below_only, income < income_limit, income <= income_limit)
