from policyengine_us.model_api import *


class ri_employer_job_development_fund_tax(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island employer job development fund tax"
    documentation = "Employer-side Rhode Island Job Development Fund assessment."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI

    def formula(person, period, parameters):
        rate = parameters(
            period
        ).gov.states.ri.tax.payroll.job_development_fund.employer_rate
        return rate * person("taxable_earnings_for_state_unemployment_tax", period)
