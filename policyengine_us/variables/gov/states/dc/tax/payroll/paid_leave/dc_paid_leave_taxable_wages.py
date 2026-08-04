from policyengine_us.model_api import *


class dc_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "DC paid leave taxable wages"
    documentation = (
        "Wages subject to the District of Columbia paid leave employer tax, "
        "including federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        return max_(0, person("employment_income", period))


class employer_total_dc_paid_leave_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total DC paid leave taxable wages"
    documentation = (
        "Aggregate employer wages subject to the District of Columbia paid "
        "leave employer tax for employer-only payroll tax calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        return person("employer_total_payroll_tax_gross_wages", period)
