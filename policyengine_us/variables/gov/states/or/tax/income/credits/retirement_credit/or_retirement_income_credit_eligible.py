from policyengine_us.model_api import *


class or_retirement_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Oregon Retirement Income Tax Credit"
    definition_period = YEAR
    reference = "https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=238290#:~:text=Eligible%20individuals%20receiving%20retirement%20pay,by%20the%20household%20income%20limitation."
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        # The filer or spouse have to be over 61 for their pension income to count
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        p = (parameters(period).gov.states["or"].tax.income.credits.retirement_income)
        head_eligible = (age >= p.age_eligibility) & head
        spouse_eligible = (age >= p.age_eligibility) & spouse
        return head_eligible | spouse_eligible
