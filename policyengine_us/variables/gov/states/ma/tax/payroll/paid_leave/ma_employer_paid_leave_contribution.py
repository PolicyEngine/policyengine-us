from policyengine_us.model_api import *


class ma_employer_paid_leave_contribution(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts employer paid leave contribution"
    documentation = (
        "Employer-side Massachusetts Paid Family and Medical Leave "
        "contribution: the part of each contribution the employer may not "
        "deduct, for employers with 25 or more covered individuals (employer "
        "headcount is the proxy), plus the part of the permitted employee "
        "share the employer does not deduct, which it must still remit "
        "(458 CMR 2.05(5))."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXXII/Chapter175M/Section6",
        "https://malegislature.gov/Laws/SessionLaws/Acts/2026/Chapter101",
        "https://www.mass.gov/doc/458-cmr-2-family-and-medical-leave/download#page=12",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        employer_rate = p.family_rate * (
            1 - p.family_employee_share
        ) + p.medical_rate * (1 - p.medical_employee_share)
        employee_rate = (
            p.family_rate * p.family_employee_share
            + p.medical_rate * p.medical_employee_share
        )
        taxable_wages = person("ma_paid_leave_taxable_wages", period)
        employer_share = where(liable, employer_rate * taxable_wages, 0)
        undeducted = 1 - person("state_payroll_premium_deduction_share", period)
        return employer_share + undeducted * employee_rate * taxable_wages
