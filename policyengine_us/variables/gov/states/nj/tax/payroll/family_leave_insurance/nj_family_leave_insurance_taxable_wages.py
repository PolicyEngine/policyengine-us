from policyengine_us.model_api import *


class nj_family_leave_insurance_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey family leave insurance taxable wages"
    documentation = (
        "Wages subject to New Jersey family leave insurance contributions, "
        "including federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll
        return min_(
            max_(0, person("employment_income", period)),
            p.temporary_disability_insurance.taxable_wage_base,
        )
