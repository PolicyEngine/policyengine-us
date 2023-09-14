from policyengine_us.model_api import *


class social_security_taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income for computing Social Security tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        ss_cap = parameters(period).gov.irs.payroll.social_security.cap
        # Deduct SS payroll taxable wages and salaries.
        return min_(
            person("taxable_self_employment_income", period),
            ss_cap - person("taxable_earnings_for_social_security", period),
        )
