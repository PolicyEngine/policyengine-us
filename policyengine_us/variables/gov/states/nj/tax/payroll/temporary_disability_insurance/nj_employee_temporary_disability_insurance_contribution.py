from policyengine_us.model_api import *


class nj_employee_temporary_disability_insurance_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee temporary disability insurance contribution"
    documentation = (
        "Employee-side New Jersey temporary disability insurance contribution."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.temporary_disability_insurance
        taxable_wages = person(
            "nj_temporary_disability_insurance_taxable_wages", period
        )
        return p.employee_rate * taxable_wages
