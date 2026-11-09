from policyengine_us.model_api import *


class ri_employer_job_development_fund_tax(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island employer job development fund tax"
    documentation = (
        "Employer-side Rhode Island job development assessment, including the "
        "job development assessment adjustment that applied in 2019."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE28/28-43/28-43-8.5.htm"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.tax.payroll.job_development_fund
        rate = p.employer_rate + p.adjustment_rate
        return rate * person("taxable_earnings_for_state_unemployment_tax", period)
