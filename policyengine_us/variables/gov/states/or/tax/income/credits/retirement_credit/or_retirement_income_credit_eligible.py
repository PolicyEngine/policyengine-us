from policyengine_us.model_api import *


class or_retirement_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Oregon Retirement Income Tax Credit"
    definition_period = YEAR
    reference = "https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=238290#:~:text=Eligible%20individuals%20receiving%20retirement%20pay,by%20the%20household%20income%20limitation."
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        # taxpayer or spouse must be age 62+ for their pension income to count
        age = person("age", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.retirement_income
        )
        return (age >= p.age_eligibility) & (is_head | is_spouse)
