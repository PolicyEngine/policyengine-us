from policyengine_us.model_api import *


class vt_employer_child_care_contribution(Variable):
    value_type = float
    entity = Person
    label = "Vermont employer child care contribution"
    documentation = (
        "Employer-side Vermont Child Care Contribution: the three quarters the "
        "employer may not withhold, plus the part of the permitted employee "
        "quarter it does not withhold, for which it is responsible "
        "(32 V.S.A. s. 10553(c)(2))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.VT
    reference = "https://legislature.vermont.gov/statutes/section/32/246/10553"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.tax.payroll.child_care
        wages = person("vt_child_care_contribution_wages", period)
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return (p.employer_rate + undeducted * p.employee_rate) * wages
