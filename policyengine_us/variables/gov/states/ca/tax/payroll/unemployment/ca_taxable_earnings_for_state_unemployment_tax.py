from policyengine_us.model_api import *


class ca_taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "California taxable earnings for state unemployment tax"
    documentation = (
        "Earnings subject to the California employer-side state unemployment "
        "insurance tax base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return min_(
            person("ca_payroll_tax_gross_wages", period),
            parameters(period).gov.states.ca.tax.payroll.unemployment.taxable_wage_base,
        )
