from policyengine_us.model_api import *


class social_security_taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income for computing Social Security tax"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#b"

    def formula(person, period, parameters):
        ss_wage_base = parameters(
            period
        ).gov.ssa.social_security.contribution_and_benefit_base
        # This will not be negative, since
        # taxable_earnings_for_social_security is capped at the wage base.
        cap_minus_earnings = ss_wage_base - person(
            "taxable_earnings_for_social_security", period
        )
        # Deduct SS payroll taxable wages and salaries.
        return min_(
            person("taxable_self_employment_income", period),
            cap_minus_earnings,
        )
