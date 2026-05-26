from policyengine_us.model_api import *


class vt_child_care_contribution_wages(Variable):
    value_type = float
    entity = Person
    label = "Vermont child care contribution wages"
    documentation = (
        "Wages subject to Vermont Child Care Contribution, following the "
        "income tax withholding wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        return person("irs_employment_income", period)


class employer_total_vt_child_care_contribution_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Vermont child care contribution wages"
    documentation = (
        "Aggregate employer wages subject to Vermont Child Care Contribution "
        "for employer-only payroll tax calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        return person("employer_total_payroll_tax_gross_wages", period)
