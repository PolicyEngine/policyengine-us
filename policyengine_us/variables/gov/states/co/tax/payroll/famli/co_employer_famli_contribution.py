from policyengine_us.model_api import *


class co_employer_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Colorado employer FAMLI contribution"
    documentation = "Employer-side Colorado FAMLI payroll contribution."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.payroll.famli
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("taxable_earnings_for_social_security", period)
        return where(liable, p.employer_rate * taxable_wages, 0)
