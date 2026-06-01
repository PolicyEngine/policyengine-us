from policyengine_us.model_api import *


class nj_temporary_disability_insurance_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey temporary disability insurance taxable wages"
    documentation = (
        "Wages subject to New Jersey temporary disability insurance "
        "contributions, including federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.temporary_disability_insurance
        return min_(max_(0, person("employment_income", period)), p.taxable_wage_base)
