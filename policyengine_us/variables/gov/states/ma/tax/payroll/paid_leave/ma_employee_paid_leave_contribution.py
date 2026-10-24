from policyengine_us.model_api import *


class ma_employee_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employee paid leave contribution"
    documentation = (
        "Employee-side Massachusetts Paid Family and Medical Leave "
        "contribution. The employer remits the contribution and may deduct up "
        "to a capped share of the family and the medical contribution from "
        "wages (M.G.L. c. 175M s. 6(c)-(d)); this is that permitted share "
        "times state_payroll_premium_deduction_share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXII/Chapter175M/Section6",
        "https://malegislature.gov/Laws/SessionLaws/Acts/2026/Chapter101",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        rate = (
            p.family_rate * p.family_employee_share
            + p.medical_rate * p.medical_employee_share
        )
        permitted = rate * person("ma_paid_leave_taxable_wages", period)
        return permitted * person("state_payroll_premium_deduction_share", period)
