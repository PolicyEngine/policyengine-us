from policyengine_us.model_api import *


class taxable_earnings_for_social_security(Variable):
    value_type = float
    entity = Person
    label = "Taxable gross earnings for OASDI FICA"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        ss_wage_base = parameters(
            period
        ).gov.ssa.social_security.contribution_and_benefit_base
        return min_(ss_wage_base, person("payroll_tax_gross_wages", period))
