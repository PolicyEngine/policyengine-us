from policyengine_us.model_api import *


class ma_ccfa_countable_income_person(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts CCFA countable income for a person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=37",
        "https://www.mass.gov/doc/interim-income-eligible-child-care-financial-assistance-program-policies-october-1-2023/download#page=12",
        "https://www.mass.gov/doc/eec-policy-advisory-field-operations-2023-4-child-care-financial-assistance/download#page=3",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.income.countable_income
        gross = add(person, period, p.sources.earned + p.sources.unearned)
        is_parent = person("ma_ccfa_is_parent", period.this_year)
        earned = add(person, period, p.sources.earned)
        if p.exclusions.minor_earnings_in_effect:
            minor = person("is_child", period.this_year)
            gross -= where(minor, earned, 0)

        if p.only_parent_income_in_effect:
            return where(is_parent, gross, 0)

        # Support paid is deducted from aggregated household income in
        # ma_ccfa_countable_income, without capping it at the payer's income.
        dependent = person("is_tax_unit_dependent", period.this_year)
        dependent_income = where(dependent, max_(gross - earned, 0), 0)
        return where(is_parent, gross, dependent_income)
