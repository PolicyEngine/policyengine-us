from policyengine_us.model_api import *


class ma_taxable_earnings_for_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts taxable earnings for state unemployment tax"
    documentation = (
        "Earnings subject to the Massachusetts employer-side state "
        "unemployment insurance tax base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        return min_(
            max_(0, person("employment_income", period)),
            parameters(period).gov.states.ma.tax.payroll.unemployment.taxable_wage_base,
        )
