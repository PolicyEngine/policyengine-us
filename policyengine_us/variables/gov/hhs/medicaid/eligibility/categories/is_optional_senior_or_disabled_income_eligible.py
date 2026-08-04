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
        "income disregard does not exceed the income limit that the state sets "
        "for its optional pathway for aged, blind, or disabled individuals who "
        "are not otherwise SSI-eligible. The limits are income maxima, so "
        "income exactly equal to the limit qualifies."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        personal_income = person(
            "medicaid_optional_senior_or_disabled_countable_income", period
        )
        income = person.tax_unit.sum(personal_income)
        income_limit = person(
            "medicaid_optional_senior_or_disabled_income_limit", period
        )
        return income <= income_limit
