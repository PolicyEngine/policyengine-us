from policyengine_us.model_api import *


class vt_employee_child_care_contribution(Variable):
    value_type = float
    entity = Person
    label = "Vermont employee child care contribution"
    documentation = (
        "Employee-side Vermont Child Care Contribution, assuming the employer "
        "withholds the maximum permitted employee share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.vt.tax.payroll.child_care.employee_rate
        return rate * person("payroll_tax_gross_wages", period)
