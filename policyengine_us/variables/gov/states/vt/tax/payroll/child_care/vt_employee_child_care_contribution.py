from policyengine_us.model_api import *


class vt_employee_child_care_contribution(Variable):
    value_type = float
    entity = Person
    label = "Vermont employee child care contribution"
    documentation = (
        "Employee-side Vermont Child Care Contribution. The employer pays the "
        "contribution and may withhold up to a quarter of it from wages "
        "(32 V.S.A. s. 10553(a)(1)); this is that permitted share times "
        "state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT
    reference = "https://legislature.vermont.gov/statutes/section/32/246/10553"

    def formula(person, period, parameters):
        rate = parameters(period).gov.states.vt.tax.payroll.child_care.employee_rate
        permitted = rate * person("vt_child_care_contribution_wages", period)
        return permitted * person("state_payroll_premium_deduction_share", period)
