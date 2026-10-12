from policyengine_us.model_api import *


class ri_taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island taxable earnings for state unemployment tax"
    documentation = (
        "Earnings subject to the Rhode Island employer-side state "
        "unemployment insurance tax base, following the income tax wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI

    def formula(person, period, parameters):
        return min_(
            person("irs_employment_income", period),
            parameters(period).gov.states.ri.tax.payroll.unemployment.taxable_wage_base,
        )
