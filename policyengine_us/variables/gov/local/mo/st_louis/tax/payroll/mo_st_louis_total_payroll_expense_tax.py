from policyengine_us.model_api import *


class mo_st_louis_total_payroll_expense_tax(Variable):
    value_type = float
    entity = Person
    label = "Total St. Louis payroll expense tax"
    documentation = (
        "Employer-side St. Louis payroll expense tax liability from aggregate "
        "taxable payroll expense inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.stlouis-mo.gov/government/departments/collector/"
        "earnings-tax/payroll-tax-info.cfm"
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        payroll_expense = person("employer_total_mo_st_louis_payroll_expense", period)
        rate = parameters(period).gov.local.mo.st_louis.tax.payroll.payroll_expense.rate
        return where(state_code == StateCode.MO, rate * payroll_expense, 0)
