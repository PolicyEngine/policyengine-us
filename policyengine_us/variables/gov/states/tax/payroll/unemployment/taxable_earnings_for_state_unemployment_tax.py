from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    select_state_unemployment_tax_parameter,
)


class taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Taxable earnings for state unemployment tax"
    documentation = (
        "Earnings subject to the employer-side state unemployment insurance "
        "tax base, using household state as a proxy for work state."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        wage_base = select_state_unemployment_tax_parameter(
            person, period, parameters, "taxable_wage_base"
        )
        return min_(person("payroll_tax_gross_wages", period), wage_base)
