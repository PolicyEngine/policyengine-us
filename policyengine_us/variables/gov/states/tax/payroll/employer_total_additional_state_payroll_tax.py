from policyengine_us.model_api import *


class employer_total_additional_state_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total additional state payroll taxes and contributions"
    documentation = (
        "Employer-level state payroll taxes and contributions other than "
        "state unemployment insurance, from aggregate employer inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        headcount = person("employer_headcount", period)
        gross_wages = person("employer_total_payroll_tax_gross_wages", period)
        ss_taxable = person(
            "employer_total_taxable_earnings_for_social_security", period
        )
        state_ui_taxable = person(
            "employer_total_taxable_earnings_for_state_unemployment_tax", period
        )

        ca = (
            parameters(
                period
            ).gov.states.ca.tax.payroll.employment_training.employer_rate
            * state_ui_taxable
        )

        co_p = parameters(period).gov.states.co.tax.payroll.famli
        co = where(
            headcount >= co_p.employer_headcount_threshold,
            co_p.employer_rate * ss_taxable,
            0,
        )

        dc = (
            parameters(period).gov.states.dc.tax.payroll.paid_leave.employer_rate
            * gross_wages
        )

        de_p = parameters(period).gov.states.de.tax.payroll.paid_leave
        de_full_coverage_rate = (
            de_p.family_caregiver_rate + de_p.medical_rate + de_p.parental_rate
        )
        de_contribution_rate = select(
            [
                headcount < de_p.small_employer_threshold,
                headcount < de_p.full_coverage_threshold,
            ],
            [0, de_p.parental_rate],
            default=de_full_coverage_rate,
        )
        de = de_contribution_rate * (1 - de_p.employee_share) * ss_taxable

        ma_p = parameters(period).gov.states.ma.tax.payroll.paid_leave
        ma = where(
            headcount >= ma_p.employer_headcount_threshold,
            ma_p.medical_rate * (1 - ma_p.medical_employee_share) * ss_taxable,
            0,
        )

        me_p = parameters(period).gov.states.me.tax.payroll.paid_leave
        me = where(
            headcount >= me_p.employer_headcount_threshold,
            me_p.employer_rate * ss_taxable,
            0,
        )

        or_p = parameters(period).gov.states["or"].tax.payroll.paid_leave
        or_tax = where(
            headcount >= or_p.employer_headcount_threshold,
            or_p.employer_rate * ss_taxable,
            0,
        )

        ri = (
            parameters(
                period
            ).gov.states.ri.tax.payroll.job_development_fund.employer_rate
            * state_ui_taxable
        )

        vt = (
            parameters(period).gov.states.vt.tax.payroll.child_care.employer_rate
            * gross_wages
        )

        wa_p = parameters(period).gov.states.wa.tax.payroll.paid_leave
        wa = where(
            headcount >= wa_p.employer_headcount_threshold,
            wa_p.total_rate * wa_p.employer_share * ss_taxable,
            0,
        )

        return select(
            [
                state_code == StateCode.CA,
                state_code == StateCode.CO,
                state_code == StateCode.DC,
                state_code == StateCode.DE,
                state_code == StateCode.MA,
                state_code == StateCode.ME,
                state_code == StateCode.OR,
                state_code == StateCode.RI,
                state_code == StateCode.VT,
                state_code == StateCode.WA,
            ],
            [ca, co, dc, de, ma, me, or_tax, ri, vt, wa],
            default=0,
        )
