from policyengine_us.model_api import *


class taxable_earnings_for_federal_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Taxable earnings for federal unemployment tax"
    documentation = "Earnings subject to the federal unemployment tax base."
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        federal_unemployment = parameters(period).gov.irs.payroll.federal_unemployment
        wage_base = federal_unemployment.taxable_wage_base
        return min_(person("payroll_tax_gross_wages", period), wage_base)
