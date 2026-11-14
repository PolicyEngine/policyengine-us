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
        employer_rate = person("vt_employer_child_care_contribution_rate", period)
        employee_rate = person("vt_employee_child_care_contribution_rate", period)
        wages = person("vt_child_care_contribution_wages", period)
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return (employer_rate + undeducted * employee_rate) * wages
